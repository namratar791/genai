import json
from clients.client import (
    mcp_client
)


class SchemaAgent:

    async def run( self, question: str, datasource: str ):

        result = await (
            mcp_client.retrieve_schema(
                question,
                datasource
            )
        )
        response = result

        return response