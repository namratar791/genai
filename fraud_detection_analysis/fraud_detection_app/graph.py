from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from agent_client import post_a2a_task
from fallbacks import (
    action_fallback,
    behavior_fallback,
    confidence_fallback,
    device_fallback,
    guardrail_fallback,
    hil_fallback,
    location_fallback,
    merchant_fallback,
    policy_fallback,
    vpn_fallback,
)
from llm import (
    build_action_llm,
    build_confidence_llm,
    build_guardrail_llm,
    build_hil_llm,
    build_policy_llm,
)
from prompts import (
    ACTION_SYSTEM_PROMPT,
    ACTION_USER_TEMPLATE,
    CONFIDENCE_SYSTEM_PROMPT,
    CONFIDENCE_USER_TEMPLATE,
    GUARDRAIL_SYSTEM_PROMPT,
    GUARDRAIL_USER_TEMPLATE,
    HIL_SYSTEM_PROMPT,
    HIL_USER_TEMPLATE,
    POLICY_SYSTEM_PROMPT,
    POLICY_USER_TEMPLATE,
)
from state import FraudState

BEHAVIOR_URL = "http://localhost:8001/tasks/send"
LOCATION_URL = "http://localhost:8002/tasks/send"
MERCHANT_URL = "http://localhost:8003/tasks/send"
DEVICE_URL = "http://localhost:8004/tasks/send"
VPN_URL = "http://localhost:8005/tasks/send"

policy_llm = build_policy_llm()
confidence_llm = build_confidence_llm()
action_llm = build_action_llm()
guardrail_llm = build_guardrail_llm()
hil_llm = build_hil_llm()


def _normalize_agent_events(agent_name: str, payload: dict[str, Any], fallback_status: str = "completed") -> list[dict[str, Any]]:
    raw_events = payload.get("ui_events") or []
    normalized: list[dict[str, Any]] = []

    for event in raw_events:
        normalized.append(
            {
                "event_type": event.get("event_type", "agent_update"),
                "agent": event.get("agent") or agent_name,
                "status": event.get("status", fallback_status),
                "message": event.get("message", payload.get("status_message", "Update available.")),
                "confidence_score": event.get("confidence_score"),
                "issues": event.get("issues", []),
                "handoff_to": event.get("handoff_to"),
                "final_action": event.get("final_action"),
                "final_confidence": event.get("final_confidence"),
                "final_output": event.get("final_output"),
            }
        )

    if normalized:
        return normalized

    status_message = payload.get("status_message")
    if status_message:
        return [
            {
                "event_type": "agent_result",
                "agent": agent_name,
                "status": fallback_status,
                "message": status_message,
                "confidence_score": payload.get("confidence_score"),
                "issues": payload.get("issues", []),
                "handoff_to": payload.get("handoff_to"),
                "final_action": payload.get("final_action"),
                "final_confidence": payload.get("final_confidence"),
                "final_output": payload.get("final_output"),
            }
        ]

    return []

def _is_agent_complete(result: dict[str, Any], turns: int, max_turns: int) -> bool:
    if "completed" in result:
        return bool(result["completed"])
    if result.get("needs_followup") is True:
        return False
    if turns >= max_turns:
        return True
    return True


async def orchestrator_start_node(state: FraudState) -> dict[str, Any]:
    return {
        "status": "working",
        "done": False,
        "ui_events": [
            {
                "event_type": "agent_update",
                "agent": "orchestrator",
                "status": "working",
                "message": "Autonomous review initialized. Parallel agent coordination started.",
                "handoff_to": "parallel_agents",
            }
        ],
    }


async def behavior_agent_cycle(state: FraudState) -> dict[str, Any]:
    turns = state.get("behavior_turns", 0) + 1
    payload = {
        **state["request"],
        "peer_context": {
            "location_result": state.get("location_result"),
            "merchant_result": state.get("merchant_result"),
            "device_result": state.get("device_result"),
            "vpn_result": state.get("vpn_result"),
        },
        "self_context": state.get("behavior_result"),
        "turn_index": turns,
    }
    try:
        result = await post_a2a_task(
            url=BEHAVIOR_URL,
            payload=payload,
            requested_skill="behavior_analysis",
            from_agent="orchestrator",
            timeout_seconds=15.0,
        )
    except Exception:
        result = behavior_fallback()

    return {
        "behavior_result": result,
        "behavior_turns": turns,
        "behavior_done": _is_agent_complete(result, turns, state.get("max_parallel_turns", 2)),
        "ui_events": _normalize_agent_events("behavior_agent", result),
    }


async def location_agent_cycle(state: FraudState) -> dict[str, Any]:
    turns = state.get("location_turns", 0) + 1
    payload = {
        **state["request"],
        "peer_context": {
            "behavior_result": state.get("behavior_result"),
            "merchant_result": state.get("merchant_result"),
            "device_result": state.get("device_result"),
            "vpn_result": state.get("vpn_result"),
        },
        "self_context": state.get("location_result"),
        "turn_index": turns,
    }
    try:
        result = await post_a2a_task(
            url=LOCATION_URL,
            payload=payload,
            requested_skill="geo_analysis",
            from_agent="orchestrator",
            timeout_seconds=15.0,
        )
    except Exception:
        result = location_fallback()

    return {
        "location_result": result,
        "location_turns": turns,
        "location_done": _is_agent_complete(result, turns, state.get("max_parallel_turns", 2)),
        "ui_events": _normalize_agent_events("location_agent", result),
    }


async def merchant_agent_cycle(state: FraudState) -> dict[str, Any]:
    turns = state.get("merchant_turns", 0) + 1
    payload = {
        **state["request"],
        "peer_context": {
            "behavior_result": state.get("behavior_result"),
            "location_result": state.get("location_result"),
            "device_result": state.get("device_result"),
            "vpn_result": state.get("vpn_result"),
        },
        "self_context": state.get("merchant_result"),
        "turn_index": turns,
    }
    try:
        result = await post_a2a_task(
            url=MERCHANT_URL,
            payload=payload,
            requested_skill="merchant_analysis",
            from_agent="orchestrator",
            timeout_seconds=15.0,
        )
    except Exception:
        result = merchant_fallback()

    return {
        "merchant_result": result,
        "merchant_turns": turns,
        "merchant_done": _is_agent_complete(result, turns, state.get("max_parallel_turns", 2)),
        "ui_events": _normalize_agent_events("merchant_agent", result),
    }


async def device_agent_cycle(state: FraudState) -> dict[str, Any]:
    turns = state.get("device_turns", 0) + 1
    payload = {
        **state["request"],
        "peer_context": {
            "behavior_result": state.get("behavior_result"),
            "location_result": state.get("location_result"),
            "merchant_result": state.get("merchant_result"),
            "vpn_result": state.get("vpn_result"),
        },
        "self_context": state.get("device_result"),
        "turn_index": turns,
    }
    try:
        result = await post_a2a_task(
            url=DEVICE_URL,
            payload=payload,
            requested_skill="device_analysis",
            from_agent="orchestrator",
            timeout_seconds=15.0,
        )
    except Exception:
        result = device_fallback()

    return {
        "device_result": result,
        "device_turns": turns,
        "device_done": _is_agent_complete(result, turns, state.get("max_parallel_turns", 2)),
        "ui_events": _normalize_agent_events("device_agent", result),
    }


async def vpn_agent_cycle(state: FraudState) -> dict[str, Any]:
    turns = state.get("vpn_turns", 0) + 1
    payload = {
        **state["request"],
        "peer_context": {
            "behavior_result": state.get("behavior_result"),
            "location_result": state.get("location_result"),
            "merchant_result": state.get("merchant_result"),
            "device_result": state.get("device_result"),
        },
        "self_context": state.get("vpn_result"),
        "turn_index": turns,
    }
    try:
        result = await post_a2a_task(
            url=VPN_URL,
            payload=payload,
            requested_skill="vpn_analysis",
            from_agent="orchestrator",
            timeout_seconds=15.0,
        )
    except Exception:
        result = vpn_fallback()

    return {
        "vpn_result": result,
        "vpn_turns": turns,
        "vpn_done": _is_agent_complete(result, turns, state.get("max_parallel_turns", 2)),
        "ui_events": _normalize_agent_events("vpn_agent", result),
    }


async def interaction_supervisor_node(state: FraudState) -> dict[str, Any]:
    required = {
        "behavior": state.get("behavior_done", False),
        "location": state.get("location_done", False),
        "merchant": state.get("merchant_done", False),
        "device": state.get("device_done", False),
        "vpn": state.get("vpn_done", False),
    }

    if all(required.values()):
        return {"status": "working", "ui_events": []}

    waiting_for = [f"{k}_agent" for k, done in required.items() if not done]
    total_turns = sum(state.get(f"{k}_turns", 0) for k in required)

    if waiting_for and total_turns > 1:
        return {
            "status": "working",
            "ui_events": [
                {
                    "event_type": "agent_update",
                    "agent": "orchestrator",
                    "status": "waiting",
                    "message": f"Waiting for remaining parallel analysis: {', '.join(waiting_for)}.",
                    "handoff_to": waiting_for[0],
                }
            ],
        }

    return {"status": "working", "ui_events": []}


async def merge_node(state: FraudState) -> dict[str, Any]:
    results = [
        state.get("behavior_result"),
        state.get("location_result"),
        state.get("merchant_result"),
        state.get("device_result"),
        state.get("vpn_result"),
    ]
    issues: list[str] = []
    risk_scores: list[float] = []

    for result in results:
        if not result:
            continue
        issues.extend(result.get("issues", []))
        if result.get("risk_score") is not None:
            risk_scores.append(float(result["risk_score"]))

    merged_result = {
        "issues": sorted(set(issues)),
        "average_risk_score": round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else None,
    }

    return {
        "merged_result": merged_result,
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "merge_node",
                "status": "completed",
                "message": "Merged specialist outputs for policy synthesis.",
                "handoff_to": "policy_node",
            }
        ],
    }


async def policy_node(state: FraudState) -> dict[str, Any]:
    try:
        prompt = POLICY_USER_TEMPLATE.format(
            behavior_result=state.get("behavior_result"),
            location_result=state.get("location_result"),
            merchant_result=state.get("merchant_result"),
            device_result=state.get("device_result"),
            vpn_result=state.get("vpn_result"),
            merged_result=state.get("merged_result"),
        )
        result = await policy_llm.ainvoke(
            [
                {"role": "system", "content": POLICY_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        policy_result = result.model_dump()
    except Exception:
        policy_result = policy_fallback()

    return {
        "policy_result": policy_result,
        "ui_events": _normalize_agent_events("policy_node", policy_result),
    }


async def confidence_node(state: FraudState) -> dict[str, Any]:
    try:
        prompt = CONFIDENCE_USER_TEMPLATE.format(
            policy_result=state.get("policy_result"),
            agent_completion_summary={
                "behavior_done": state.get("behavior_done"),
                "location_done": state.get("location_done"),
                "merchant_done": state.get("merchant_done"),
                "device_done": state.get("device_done"),
                "vpn_done": state.get("vpn_done"),
            },
            fallback_summary={
                "behavior_fallback": bool((state.get("behavior_result") or {}).get("fallback")),
                "location_fallback": bool((state.get("location_result") or {}).get("fallback")),
                "merchant_fallback": bool((state.get("merchant_result") or {}).get("fallback")),
                "device_fallback": bool((state.get("device_result") or {}).get("fallback")),
                "vpn_fallback": bool((state.get("vpn_result") or {}).get("fallback")),
            },
        )
        result = await confidence_llm.ainvoke(
            [
                {"role": "system", "content": CONFIDENCE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        confidence_result = result.model_dump()
    except Exception:
        confidence_result = confidence_fallback()

    return {
        "confidence_result": confidence_result,
        "confidence_score": confidence_result.get("confidence_score"),
        "ui_events": _normalize_agent_events("confidence_node", confidence_result),
    }


async def action_node(state: FraudState) -> dict[str, Any]:
    try:
        prompt = ACTION_USER_TEMPLATE.format(
            request_payload=state["request"],
            policy_result=state.get("policy_result"),
            confidence_result=state.get("confidence_result"),
        )
        result = await action_llm.ainvoke(
            [
                {"role": "system", "content": ACTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        action_result = result.model_dump()
    except Exception:
        action_result = action_fallback()

    return {
        "action_result": action_result,
        "ui_events": _normalize_agent_events("action_node", action_result),
    }


async def guardrail_node(state: FraudState) -> dict[str, Any]:
    try:
        prompt = GUARDRAIL_USER_TEMPLATE.format(
            policy_result=state.get("policy_result"),
            confidence_result=state.get("confidence_result"),
            action_result=state.get("action_result"),
        )
        result = await guardrail_llm.ainvoke(
            [
                {"role": "system", "content": GUARDRAIL_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        guardrail_result = result.model_dump()
    except Exception:
        guardrail_result = guardrail_fallback()

    return {
        "guardrail_result": guardrail_result,
        "final_action": guardrail_result.get("validated_action", "REVIEW"),
        "ui_events": _normalize_agent_events("guardrail_node", guardrail_result),
    }


async def hil_node(state: FraudState) -> dict[str, Any]:
    try:
        prompt = HIL_USER_TEMPLATE.format(
            request_payload=state["request"],
            policy_result=state.get("policy_result"),
            confidence_result=state.get("confidence_result"),
            action_result=state.get("action_result"),
        )
        result = await hil_llm.ainvoke(
            [
                {"role": "system", "content": HIL_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        hil_result = result.model_dump()
    except Exception:
        hil_result = hil_fallback()

    return {
        "hil_result": hil_result,
        "ui_events": _normalize_agent_events("human_review", hil_result),
    }


async def finalize_node(state: FraudState) -> dict[str, Any]:
    final_output = {
        "risk_score": (state.get("policy_result") or {}).get("risk_score"),
        "confidence_score": state.get("confidence_score"),
        "review_reason": (state.get("hil_result") or {}).get("review_reason"),
    }

    return {
        "status": "completed",
        "done": True,
        "final_response": {
            "decision": state.get("final_action"),
            "confidence": state.get("confidence_score"),
            "risk_score": (state.get("policy_result") or {}).get("risk_score"),
            "review_reason": (state.get("hil_result") or {}).get("review_reason"),
        },
        "ui_events": [
            {
                "event_type": "final_response",
                "agent": "orchestrator",
                "status": "completed",
                "message": f"Final decision ready: {state.get('final_action')}.",
                "final_action": state.get("final_action"),
                "final_confidence": state.get("confidence_score"),
                "final_output": final_output,
            }
        ],
    }


def route_after_supervisor(state: FraudState) -> str:
    required = [
        ("behavior_a2a", state.get("behavior_done", False), state.get("behavior_turns", 0)),
        ("location_a2a", state.get("location_done", False), state.get("location_turns", 0)),
        ("merchant_a2a", state.get("merchant_done", False), state.get("merchant_turns", 0)),
        ("device_a2a", state.get("device_done", False), state.get("device_turns", 0)),
        ("vpn_a2a", state.get("vpn_done", False), state.get("vpn_turns", 0)),
    ]

    incomplete = [item for item in required if not item[1]]

    if not incomplete:
        return "merge"

    # pick the unfinished agent with the fewest turns
    incomplete.sort(key=lambda x: x[2])
    return incomplete[0][0]
def route_after_guardrail(state: FraudState) -> str:
    if state.get("final_action") == "REVIEW":
        return "hil"
    return "finalize"


def build_graph():
    graph = StateGraph(FraudState)

    graph.add_node("orchestrator_start", orchestrator_start_node)
    graph.add_node("behavior_a2a", behavior_agent_cycle)
    graph.add_node("location_a2a", location_agent_cycle)
    graph.add_node("merchant_a2a", merchant_agent_cycle)
    graph.add_node("device_a2a", device_agent_cycle)
    graph.add_node("vpn_a2a", vpn_agent_cycle)
    graph.add_node("interaction_supervisor", interaction_supervisor_node)
    graph.add_node("merge", merge_node)
    graph.add_node("policy", policy_node)
    graph.add_node("confidence", confidence_node)
    graph.add_node("action", action_node)
    graph.add_node("guardrail", guardrail_node)
    graph.add_node("hil", hil_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "orchestrator_start")
    graph.add_edge("orchestrator_start", "behavior_a2a")
    graph.add_edge("orchestrator_start", "location_a2a")
    graph.add_edge("orchestrator_start", "merchant_a2a")
    graph.add_edge("orchestrator_start", "device_a2a")
    graph.add_edge("orchestrator_start", "vpn_a2a")

    graph.add_edge("behavior_a2a", "interaction_supervisor")
    graph.add_edge("location_a2a", "interaction_supervisor")
    graph.add_edge("merchant_a2a", "interaction_supervisor")
    graph.add_edge("device_a2a", "interaction_supervisor")
    graph.add_edge("vpn_a2a", "interaction_supervisor")

    graph.add_conditional_edges(
        "interaction_supervisor",
        route_after_supervisor,
        {
            "behavior_a2a": "behavior_a2a",
            "location_a2a": "location_a2a",
            "merchant_a2a": "merchant_a2a",
            "device_a2a": "device_a2a",
            "vpn_a2a": "vpn_a2a",
            "merge": "merge",
        },
    )

    graph.add_edge("merge", "policy")
    graph.add_edge("policy", "confidence")
    graph.add_edge("confidence", "action")
    graph.add_edge("action", "guardrail")

    graph.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {
            "hil": "hil",
            "finalize": "finalize",
        },
    )

    graph.add_edge("hil", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()