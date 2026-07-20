import json
from offline.dataset_generator.prompts.prompts import ( SQL_PROMPT )

class SQLGenerationAgent:

    def __init__(self, llm):
        self.llm = llm

    async def generate(self, question, tables, metadata):
        prompt = SQL_PROMPT.format( question=question, tables=tables, metadata=metadata )
        response = await self.llm.ainvoke(prompt)
        return json.loads( response.content )