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
    peer_context: dict[str, Any] | None = None
    self_context: dict[str, Any] | None = None
    turn_index: int | None = None


class AgentUIEvent(BaseModel):
    event_type: Literal["agent_update", "agent_result"] = "agent_update"
    status: Literal["working", "waiting", "completed", "failed"]
    message: str
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    handoff_to: str | None = None


class A2AMessagePart(BaseModel):
    type: Literal["json"] = "json"
    data: dict[str, Any]


class A2AMessage(BaseModel):
    role: Literal["user", "agent"] = "user"
    parts: list[A2AMessagePart]


class A2ATaskRequest(BaseModel):
    task_id: str
    message: A2AMessage
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentSkill(BaseModel):
    id: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class AgentCard(BaseModel):
    name: str
    description: str
    endpoint: str
    version: str
    protocol: str = "a2a-http"
    transport: str = "http"
    skills: list[AgentSkill]


class LocationOutput(BaseModel):
    agent: Literal["location_agent"] = "location_agent"
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence_score: float = Field(ge=0.0, le=1.0)
    geo_mismatch: bool | None = None
    issues: list[str] = Field(default_factory=list)
    status_message: str
    handoff_to: Literal["policy_agent", "orchestrator"] = "policy_agent"
    ui_events: list[AgentUIEvent] = Field(default_factory=list)
    completed: bool = True
    needs_followup: bool = False


class A2ATaskResponse(BaseModel):
    task_id: str
    status: Literal["working", "completed", "failed"]
    agent: str
    ui_events: list[AgentUIEvent] = Field(default_factory=list)
    result: LocationOutput
    completed: bool = True
    needs_followup: bool = False
    recommended_handoff: str | None = None
