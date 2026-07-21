from typing import Any, Literal
from pydantic import BaseModel, Field


class FraudRequest(BaseModel):
    transaction_id: str
    amount: float = Field(gt=0)
    merchant: str
    city: str
    previous_city: str
    known_device: bool = False
    device_trust_score: float = Field(ge=0.0, le=1.0)
    vpn_suspected: bool = False


class UIEvent(BaseModel):
    sequence: int
    event_type: Literal["agent_update", "agent_result", "final_response"]
    agent: str
    status: Literal["working", "waiting", "completed", "failed"]
    message: str

    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    handoff_to: str | None = None

    final_action: Literal["APPROVE", "HOLD", "ESCALATE", "REVIEW"] | None = None
    final_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    final_output: dict[str, Any] | None = None


class FinalResponse(BaseModel):
    decision: Literal["APPROVE", "HOLD", "ESCALATE", "REVIEW"] | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    risk_score: float | None = Field(default=None, ge=0.0, le=1.0)
    review_reason: str | None = None


class RunCreateResponse(BaseModel):
    run_id: str
    status: Literal["working", "completed", "failed"]


class NextStepResponse(BaseModel):
    run_id: str
    done: bool
    status: Literal["working", "waiting", "completed", "failed"]
    delivered_count: int
    ui_events: list[UIEvent]


class RunSummaryResponse(BaseModel):
    run_id: str
    status: Literal["working", "waiting", "completed", "failed"]
    done: bool
    delivered_count: int
    emitted_events: list[dict[str, Any]]
    final_action: Literal["APPROVE", "HOLD", "ESCALATE", "REVIEW"] | None = None
    final_response: FinalResponse | None = None