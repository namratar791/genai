import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from prompts.sql_prompt import build_prompt

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class SQLAgent:
    async def run(self, question: str, schema_context: dict, error: str | None = None) -> str:
        prompt = build_prompt(question, schema_context, error)
        resp = await client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}], temperature=0,
        )
        return (
            resp.choices[0].message.content
        )