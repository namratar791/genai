import asyncio
from fastmcp import Client


async def main():

    async with Client(
        "http://127.0.0.1:8001/mcp"
    ) as client:

        tools = await client.list_tools()

        print(tools)

        result = await client.call_tool(
            "retrieve_schema",
            {
                "question":
                    "List products with supplier information",

                "datasource":
                    "sales"
            }
        )

        print(result)


asyncio.run(main())