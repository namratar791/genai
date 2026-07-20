import asyncio
from dotenv import load_dotenv
from db.database import initialize_db
from fastmcp import FastMCP
from services import MCPServices
# from tools import register_tools


load_dotenv()

initialize_db()

services = MCPServices()

mcp = FastMCP(
    name="text-to-sql-mcp",
    instructions="""
    MCP Server for Text-to-SQL.
    Supports:

    - retrieve_schema
    - execute_sql
    """
)


#########################################################
# Retrieve Schema
#########################################################
@mcp.tool
async def get_schema_metadata( datasource: str ) -> any:
    print("inisde.....")
    return await services.get_schema_metadata(
        datasource
    )

@mcp.tool(
    annotations={
        "skill": "query",
        "tags": [
            "schema",
            "metadata",
            "vector-search"
        ]
    }
)
async def retrieve_schema(
    question: str,
    datasource: str
) -> dict:
    """
    Retrieve relevant tables, columns and relationships
    for a natural language question.
    """

    if not question:
        raise ValueError(
            "question cannot be empty"
        )

    if not datasource:
        raise ValueError(
            "datasource cannot be empty"
        )

    return await services.retrieve_schema(
        question=question,
        datasource=datasource
    )

#########################################################
# Execute SQL
#########################################################

@mcp.tool(
    annotations={
        "skill": "query",
        "tags": [
            "sql",
            "execution"
        ]
    }
)
async def execute_sql(
    sql: str,
    datasource: str
) -> any:
   
    if not sql:
        raise ValueError(
            "sql cannot be empty"
        )

    if not datasource:
        raise ValueError(
            "datasource cannot be empty"
        )
    rows = await services.execute_sql( sql=sql, datasource=datasource )
    return {
        "status": "success",
        "rows": rows,
        "count": len(rows)
    }

#########################################################
# Optional Future Tool
#########################################################

@mcp.tool(
    annotations={
        "skill": "admin",
        "tags": [
            "metadata",
            "ingestion"
        ]
    }
)
async def refresh_metadata(
    datasource: str
) -> dict:
    """
    Refresh metadata embeddings.
    """

    return await services.refresh_metadata(
        datasource
    )

#########################################################
# Optional Future Tool
#########################################################

@mcp.tool(
    annotations={
        "skill": "admin",
        "tags": [
            "datasource"
        ]
    }
)
async def get_datasources() -> list:
    """
    Return all available datasources.
    """

    return await services.get_datasources()




if __name__ == "__main__":

    print("SERVER STARTED")
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8001
    )