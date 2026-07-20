import json

from offline.dataset_generator.prompts.prompts import ( QUESTION_PROMPT )


class QuestionGenerationAgent:

    def __init__(self, llm):
        self.llm = llm


    async def generate(self, metadata, count):

        prompt = QUESTION_PROMPT.format( metadata=metadata, count=count)
        response = await self.llm.ainvoke(prompt)
        return json.loads( response.content )