import os
from langchain_openai import ChatOpenAI
from langgraph.graph import ( StateGraph,END )
from offline.dataset_generator.models.dataset_models import ( DatasetState )
from offline.dataset_generator.agents.question_generation_agent import ( QuestionGenerationAgent )
from offline.dataset_generator.agents.retrieval_label_agent import ( RetrievalLabelAgent)
from offline.dataset_generator.agents.sql_generation_agent import ( SQLGenerationAgent )
from offline.dataset_generator.agents.validation_agent import ( ValidationAgent )
from offline.dataset_generator.agents.dataset_writer_agent import ( DatasetWriterAgent )
from clients.client import mcp_client

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)
question_agent = ( QuestionGenerationAgent(llm) )
retrieval_agent = ( RetrievalLabelAgent(llm) )
sql_agent = ( SQLGenerationAgent(llm) )
validation_agent = ( ValidationAgent(mcp_client) )
writer_agent = ( DatasetWriterAgent() )

async def metadata_node( state: DatasetState ):
    metadata = await ( mcp_client.generate_metadata( state["datasource"] ))
    state["metadata"] = metadata
    return state

async def question_generation_node(state: DatasetState):
    state["questions"] = await ( question_agent.generate(state["metadata"],state["count"]))
    return state

async def retrieval_label_node(state: DatasetState):

    retrieval_dataset = []
    for item in state["questions"]:
        question = item["question"]
        result = await (retrieval_agent.generate( question, state["metadata"]))
        retrieval_dataset.append( {"question": question,"expected_tables": result["expected_tables"]} )

    state["retrieval_dataset"] = ( retrieval_dataset )
    return state

async def sql_generation_node(state: DatasetState):

    generation_dataset = []
    for item in state["retrieval_dataset"]:
        sql = await (sql_agent.generate(item["question"],item["expected_tables"],state["metadata"]))
        generation_dataset.append(
            {
                "question": item["question"],
                "expected_tables": item["expected_tables"],
                "gold_sql": sql["gold_sql"]
            })

    state["generation_dataset"] = (generation_dataset)
    return state

async def validation_node(state: DatasetState):

    valid_dataset = []
    for item in state["generation_dataset"]:
        valid = await (validation_agent.validate(item["gold_sql"],state["datasource"]))
        if valid:
            valid_dataset.append(item)
    state["generation_dataset"] = (valid_dataset)
    return state

async def writer_node(state: DatasetState):

    await writer_agent.save( state["datasource"], state["retrieval_dataset"], state["generation_dataset"] )
    return state


def build_dataset_workflow():

    graph = StateGraph( DatasetState )

    graph.add_node("question_generation_node",question_generation_node)
    graph.add_node( "retrieval_label_node", retrieval_label_node) 
    graph.add_node( "sql_generation_node",sql_generation_node )
    graph.add_node("validation_node", validation_node)
    graph.add_node( "writer_node", writer_node )

    graph.set_entry_point( "question_generation_node")
    graph.add_edge("question_generation_node","retrieval_label_node")
    graph.add_edge("retrieval_label_node", "sql_generation_node")
    graph.add_edge("sql_generation_node", "validation_node")
    graph.add_edge( "validation_node", "writer_node")
    graph.add_edge( "writer_node", END)

    return graph.compile()

# workflow = ( build_dataset_workflow() )
# result = workflow.invoke(
#     {
#         "datasource": "sales",
#         "count": 30,
#         "metadata": metadata
#     })