import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from models.request import QueryRequest
from agents.text_to_sql_agent import TextToSQLAgent
from contextlib import (
    asynccontextmanager
)
from clients.client import (
    mcp_client
)
from graph.state import RequestContext, GraphState

# app = FastAPI(title="TextToSQL Host")
agent = TextToSQLAgent()
load_dotenv()

@asynccontextmanager
async def lifespan(
    app: FastAPI
):
    print( "Initializing MCP..." )
    tools = await ( mcp_client.initialize() )
    print("hellloooo....")
    print("\n")
    print(tools)
    yield
    print( "Shutting down..." )

app = FastAPI(
    title="TextToSQL Host",
    lifespan=lifespan
)
@app.middleware("http")
async def add_request_context(
    request: Request,
    call_next
):

    request.state.request_id = "req_2"
    request.state.session_id = request.headers.get(
        "x-session-id"
    )

    # request.state.token = request.headers.get(
    #     "Authorization"
    # )

    response = await call_next(
        request
    )

    return response

@app.post("/query")
async def query(body: QueryRequest, request: Request):
    context = RequestContext(
        request_id=request.state.request_id,
        session_id=request.state.session_id,
        token=getattr(
            request.state,
            "token",
            None
        ),
        user_id="user123"
    )

    result = await agent.run(
        question=body.question,
        datasource=body.datasource,
        context=context,
        type=body.type
    )
    return {
        "answer": result.get("answer"),
        "result": result.get("result"),
        "sql": result.get("generated_sql")
    }


@app.get("/offline/refreshMetadata")
async def query(request: Request):

    result = await mcp_client.refresh_metadata("sales")
    return {
        "result": "done"
    }

# @app.get("/offline/generateDataset")
# async def query(request: Request):

#     result = await mcp_client.refresh_metadata("sales")
#     return {
#         "result": "done"
#     }
