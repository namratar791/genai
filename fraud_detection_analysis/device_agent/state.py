from typing import Any, TypedDict, NotRequired


class AgentState(TypedDict):
    request: dict[str, Any]
    analysis_result: NotRequired[dict[str, Any] | None]
    status: str
    done: bool
    error: NotRequired[str | None]
