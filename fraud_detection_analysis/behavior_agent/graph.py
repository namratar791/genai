from langgraph.graph import StateGraph, START, END

from fallbacks import behavior_fallback
from llm import build_llm
from models import FraudRequest
from prompts import SYSTEM_PROMPT, USER_TEMPLATE
from state import AgentState

llm = build_llm()


async def analyze_node(state: AgentState) -> dict:
    try:
        req = FraudRequest(**state["request"])
        prompt = USER_TEMPLATE.format(request_payload=req.model_dump())
        result = await llm.ainvoke(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        output = result.model_dump()
        return {
            "analysis_result": output,
            "status": "completed",
            "done": True,
        }
    except Exception:
        return {
            "analysis_result": behavior_fallback(),
            "status": "completed",
            "done": True,
        }


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("analyze", analyze_node)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", END)
    return graph.compile()
