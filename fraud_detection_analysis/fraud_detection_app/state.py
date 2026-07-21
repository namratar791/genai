import operator
from typing import Annotated, Any, NotRequired, TypedDict


class FraudState(TypedDict):
    # input
    request: dict[str, Any]

    # specialist agent outputs
    behavior_result: dict[str, Any] | None
    location_result: dict[str, Any] | None
    merchant_result: dict[str, Any] | None
    device_result: dict[str, Any] | None
    vpn_result: dict[str, Any] | None

    # merged / orchestration outputs
    merged_result: dict[str, Any] | None
    policy_result: dict[str, Any] | None
    confidence_result: dict[str, Any] | None
    action_result: dict[str, Any] | None
    guardrail_result: dict[str, Any] | None
    hil_result: dict[str, Any] | None
    final_response: dict[str, Any] | None

    # per-agent completion flags
    behavior_done: bool
    location_done: bool
    merchant_done: bool
    device_done: bool
    vpn_done: bool

    # optional turn counters if you keep multi-turn routing
    behavior_turns: NotRequired[int]
    location_turns: NotRequired[int]
    merchant_turns: NotRequired[int]
    device_turns: NotRequired[int]
    vpn_turns: NotRequired[int]
    max_parallel_turns: NotRequired[int]

    # decision values
    confidence_score: float
    final_action: str | None

    # safety / fallback flags
    fallback_used: NotRequired[bool]

    # UI stream
    ui_events: Annotated[list[dict[str, Any]], operator.add]

    # lifecycle
    status: str
    done: bool
    error: NotRequired[str | None]