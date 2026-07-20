import os
from langgraph.graph import StateGraph, END
from graph.state import GraphState
from agents.schema_agent import SchemaAgent
from agents.sql_agent import SQLAgent
from clients.client import MCPClient
from agents.dataset_generation_agent import DatasetGenerationAgent

schema_agent = SchemaAgent()
sql_agent = SQLAgent()
mcp_client = MCPClient()
dataset_generator_agent = DatasetGenerationAgent()
MAX_RETRIES = int(os.getenv("MAX_REPAIR_RETRIES", 2))

async def intent_node(state: GraphState) -> GraphState:
    state["intent"] = (
        state["type"]
    )
    return state

async def schema_node(state: GraphState) -> GraphState:
    state["schema_context"] = await schema_agent.run(state["question"], state["datasource"])
    return state


async def sql_node(state: GraphState) -> GraphState:
    state["generated_sql"] = await sql_agent.run(state["question"], state["schema_context"])
    return state

async def execute_node(state: GraphState) -> GraphState:
    result = await mcp_client.execute_sql(state["generated_sql"], state["datasource"])
    if result.get("status") == "success":
        state["sql_result"] = result.get("rows", [])
        state["error"] = None
    else:
        state["error"] = result.get("error", "execution failed")
    return state

async def repair_node(state: GraphState) -> GraphState:
    state["retry_count"] += 1
    state["generated_sql"] = await sql_agent.run(
        question=state["question"],
        schema_context=state["schema_context"],
        error=state["error"],
    )
    return state

async def response_node(state: GraphState) -> GraphState:
    if state.get("error"):
        state["answer"] = f"Could not complete the query: {state['error']}"
    else:
        state["answer"] = f"Query returned {len(state.get('sql_result', []))} rows."
    return state

async def feedback_node(state: GraphState) -> GraphState:
    print("feedback_node....")
    return state

async def dataset_generation_node(state: GraphState) -> GraphState:
    metadata = await mcp_client.get_schema_metadata(state["datasource"])
    await dataset_generator_agent.run(state["datasource"], metadata)
    return state
    
async def metrics_node(state: GraphState) -> GraphState:
    print("metrics_node....")
    return state

def route_after_execute(state: GraphState) -> str:
    if not state.get("error"):
        return "response_node"
    if state.get("retry_count", 0) < MAX_RETRIES:
        return "repair_node"
    return "response_node"

def route_after_intent( state: GraphState ):
    intent = ( state["intent"] )

    if intent == "TEXT_TO_SQL":
        return "schema_node"

    if intent == "DATASET_GENERATION":
        return ( "dataset_generation_node" )

    if intent == "METRICS":
        return "metrics_node"

    if intent == "NEGATIVE_FEEDBACK":
        return "feedback_node"

    raise ValueError(
        f"Unknown intent {intent}"
    )


def build_workflow():
    graph = StateGraph(GraphState)
    for name, fn in [("intent_node", intent_node), ("schema_node", schema_node), ("sql_node", sql_node),
                      ("execute_node", execute_node), ("repair_node", repair_node), ("response_node", response_node), ("dataset_generation_node",
            dataset_generation_node),("metrics_node",metrics_node),("feedback_node",feedback_node)]:
        graph.add_node(name, fn)
    graph.set_entry_point("intent_node")
    graph.add_conditional_edges("intent_node",route_after_intent,
        {
            "schema_node": "schema_node",
            "dataset_generation_node": "dataset_generation_node",
            "metrics_node": "metrics_node",
            "feedback_node": "feedback_node"
        }
    )
    graph.add_edge("schema_node", "sql_node")
    graph.add_edge("sql_node", "execute_node")
    graph.add_conditional_edges("execute_node", route_after_execute,
        {"repair_node": "repair_node", "response_node": "response_node"})
    graph.add_edge("repair_node", "execute_node")
    graph.add_edge("response_node", END)
    #################################################
    # Offline Nodes
    #################################################

    graph.add_edge( "dataset_generation_node", END )
    graph.add_edge( "metrics_node", END )
    graph.add_edge( "feedback_node",  END )

    return graph.compile()

compiled_workflow = build_workflow()