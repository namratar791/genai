import asyncio
from dotenv import load_dotenv
from fastmcp import FastMCP


app = FastMCP(name="metrics server")


@mcp.tool
async def recall()
