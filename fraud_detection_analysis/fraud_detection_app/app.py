from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from graph import build_graph
from models import FraudRequest, NextStepResponse, RunCreateResponse, RunSummaryResponse, UIEvent

app = FastAPI(title="Fraud Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()

RUNS: dict[str, dict[str, Any]] = {}


def to_ndjson(event: dict[str, Any]) -> str:
    return json.dumps(event) + "\n"


def _base_graph_state(req: FraudRequest) -> dict[str, Any]:
    return {
        "request": req.model_dump(),

        # specialist results
        "behavior_result": None,
        "location_result": None,
        "merchant_result": None,
        "device_result": None,
        "vpn_result": None,

        # merged / llm outputs
        "merged_result": None,
        "policy_result": None,
        "confidence_result": None,
        "action_result": None,
        "guardrail_result": None,
        "hil_result": None,
        "final_response": None,

        # flow flags
        "behavior_done": False,
        "location_done": False,
        "merchant_done": False,
        "device_done": False,
        "vpn_done": False,

        # confidence / decision
        "confidence_score": 0.0,
        "final_action": None,

        # UI / lifecycle
        "ui_events": [],
        "status": "working",
        "done": False,
        "error": None,
    }


def _base_run(req: FraudRequest) -> dict[str, Any]:
    return {
        "graph_state": _base_graph_state(req),
        "delivered_count": 0,
        "status": "working",
        "done": False,
        "task": None,
        "lock": asyncio.Lock(),
    }


def _append_normalized_events(run: dict[str, Any], events: list[dict[str, Any]]) -> None:
    for raw_event in events:
        payload = dict(raw_event)
        payload["sequence"] = len(run["graph_state"]["ui_events"]) + 1
        payload["agent"] = payload.get("agent") or "system"
        normalized = UIEvent(**payload).model_dump()
        run["graph_state"]["ui_events"].append(normalized)


async def _run_workflow(run_id: str) -> None:
    run = RUNS[run_id]
    initial_state = dict(run["graph_state"])

    try:
        async for update in graph.astream(initial_state, stream_mode="updates"):
            async with run["lock"]:
                for _, node_update in update.items():
                    node_payload = dict(node_update)
                    new_events = node_payload.pop("ui_events", [])

                    if new_events:
                        _append_normalized_events(run, new_events)

                    run["graph_state"].update(node_payload)
                    run["status"] = run["graph_state"].get("status", run["status"])
                    run["done"] = run["graph_state"].get("done", run["done"])

        async with run["lock"]:
            if not run["done"]:
                run["done"] = True
            run["status"] = run["graph_state"].get("status", "completed") or "completed"

    except Exception as exc:
        async with run["lock"]:
            run["graph_state"]["error"] = str(exc)
            run["status"] = "failed"
            run["done"] = True
            _append_normalized_events(
                run,
                [
                    {
                        "event_type": "final_response",
                        "agent": "orchestrator",
                        "status": "failed",
                        "message": f"Workflow failed: {exc}",
                        "final_action": "REVIEW",
                    }
                ],
            )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/fraud/runs", response_model=RunCreateResponse)
async def create_run(req: FraudRequest) -> RunCreateResponse:
    run_id = str(uuid4())
    RUNS[run_id] = _base_run(req)
    RUNS[run_id]["task"] = asyncio.create_task(_run_workflow(run_id))
    return RunCreateResponse(run_id=run_id, status="working")


@app.post("/fraud/runs/{run_id}/next", response_model=NextStepResponse)
async def next_step(run_id: str) -> NextStepResponse:
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id not found")

    async with run["lock"]:
        events = run["graph_state"].get("ui_events", [])
        delivered_count = run["delivered_count"]
        new_events = events[delivered_count:]
        run["delivered_count"] = len(events)

        return NextStepResponse(
            run_id=run_id,
            done=run["done"] and run["delivered_count"] >= len(events),
            status=run["status"],
            delivered_count=run["delivered_count"],
            ui_events=[UIEvent(**event) for event in new_events],
        )


@app.get("/fraud/runs/{run_id}", response_model=RunSummaryResponse)
async def get_run(run_id: str) -> RunSummaryResponse:
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id not found")

    final_event = run["graph_state"]["ui_events"][-1] if run["graph_state"]["ui_events"] else None
    final_response = run["graph_state"].get("final_response") or {}

    return RunSummaryResponse(
        run_id=run_id,
        status=run["status"],
        done=run["done"],
        delivered_count=run["delivered_count"],
        emitted_events=run["graph_state"].get("ui_events", []),
        final_action=final_response.get("decision") or (final_event or {}).get("final_action"),
    )


@app.post("/fraud/stream")
async def fraud_stream(req: FraudRequest):
    async def event_stream() -> AsyncGenerator[str, None]:
        initial_state = _base_graph_state(req)
        async for update in graph.astream(initial_state, stream_mode="updates"):
            for _, node_update in update.items():
                for event in node_update.get("ui_events", []):
                    yield to_ndjson(event)
                    await asyncio.sleep(0)

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )