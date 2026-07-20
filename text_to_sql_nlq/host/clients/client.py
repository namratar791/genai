import json
import os

from fastmcp import Client
from tenacity import ( retry, stop_after_attempt, wait_fixed)


MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "http://127.0.0.1:8001/mcp"
)


class MCPClient:
    def __init__(self):
        self.tools = None


    async def initialize(self):
        if self.tools:
            return
        async with Client( MCP_SERVER_URL ) as client:
            self.tools = await ( client.list_tools() )
            print("tools...", self.tools)


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2)
    )
    async def call_tool( self, tool_name: str, arguments: dict):
        async with Client( MCP_SERVER_URL ) as client:
            result = await ( client.call_tool( tool_name, arguments ))

            if hasattr( result, "structured_content" ):
                return ( result.structured_content )

            if (hasattr(result, "content" ) and result.content ):
                content = ( result.content[0] )
                if hasattr( content, "text" ):
                    try:
                        return json.loads( content.text )
                    except:
                        return ( content.text )
            return result


    async def retrieve_schema( self, question: str, datasource: str ):
        return await ( self.call_tool("retrieve_schema", {
                    "question": question,
                    "datasource": datasource
                }))


    async def execute_sql( self, sql: str, datasource: str ):
        return await ( self.call_tool( "execute_sql", {
                    "sql": sql,
                    "datasource": datasource
                }))

    async def get_schema_metadata( self, datasource):
        return await ( self.call_tool( "get_schema_metadata", {
                    "datasource": datasource
                }))

    
    async def refresh_metadata( self, datasource: str ):
        return await ( self.call_tool( "refresh_metadata", {
                    "datasource":datasource
                }))
    
    async def get_datasources( self ):
        return await (self.call_tool( "get_datasources", {}))


mcp_client = MCPClient()