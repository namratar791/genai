import json
from offline.dataset_generator.prompts.prompts import ( RETRIEVAL_PROMPT )


class RetrievalLabelAgent:

    def __init__(self, llm):
        self.llm = llm


    async def generate(self, question, metadata):

        prompt = RETRIEVAL_PROMPT.format( question=question, metadata=metadata )
        response = await self.llm.ainvoke( prompt )
        print(response,"llllll")
        return json.loads( response.content )