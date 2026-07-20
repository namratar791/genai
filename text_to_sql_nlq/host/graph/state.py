from dataclasses import dataclass
from typing import TypedDict

class RequestContext(TypedDict):
    request_id: str | None = None
    session_id: str | None = None
    token: str | None = None
    user_id: str | None = None


class GraphState(TypedDict):
    question: str
    context: RequestContext
    datasource: str
    intent: str
    schema_context: dict
    generated_sql: str
    sql_result: list
    answer: str
    error: str | None
    retry_count: int
    metrics: dict | None
    dataset_generation_request: dict | None
    type: str

