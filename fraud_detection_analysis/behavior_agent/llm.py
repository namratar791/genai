import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from models import BehaviorOutput

load_dotenv()


def build_llm() -> ChatOpenAI:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0).with_structured_output(BehaviorOutput, method="function_calling")
