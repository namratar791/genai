class ValidationAgent:

    def __init__(self, mcp_client):
        self.mcp_client = mcp_client

    async def validate(self, sql, datasource):
        try:
            await self.mcp_client.execute_sql( sql, datasource )
            return True
        except Exception:
            return False