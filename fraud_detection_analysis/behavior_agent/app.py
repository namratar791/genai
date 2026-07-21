from fastapi import FastAPI

from graph import build_graph
from models import A2ATaskRequest, A2ATaskResponse, AgentCard, AgentSkill, BehaviorOutput, FraudRequest

app = FastAPI(title="Behavior Agent")
graph = build_graph()


async def _run(req: FraudRequest) -> BehaviorOutput:
    state = {
        "request": req.model_dump(),
        "status": "working",
        "done": False,
    }
    result = await graph.ainvoke(state)
    return BehaviorOutput(**result["analysis_result"])


@app.get("/.well-known/agent-card.json", response_model=AgentCard)
async def agent_card() -> AgentCard:
    return AgentCard(
        name="behavior_agent",
        description="Analyzes transaction behavior anomalies and unusual spending patterns.",
        endpoint="http://localhost:8101/tasks/send",
        version="1.0.0",
        skills=[
            AgentSkill(
                id="behavior_analysis",
                description="Analyzes transaction behavior anomalies and unusual spending patterns.",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            )
        ],
    )


@app.post("/analyze", response_model=BehaviorOutput)
async def analyze(req: FraudRequest) -> BehaviorOutput:
    return await _run(req)


@app.post("/tasks/send", response_model=A2ATaskResponse)
async def send_task(req: A2ATaskRequest) -> A2ATaskResponse:
    payload = req.message.parts[0].data if req.message.parts else {}
    fraud_req = FraudRequest(**payload)
    result = await _run(fraud_req)
    return A2ATaskResponse(
        task_id=req.task_id,
        status="completed" if result.completed else "working",
        agent="behavior_agent",
        ui_events=result.ui_events,
        result=result,
        completed=result.completed,
        needs_followup=result.needs_followup,
        recommended_handoff=result.handoff_to,
    )
