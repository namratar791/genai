import os
from typing import Any, Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class AgentUIEvent(BaseModel):
    event_type: Literal["agent_update", "agent_result", "final_response"] = "agent_update"
    agent: str | None = None
    status: Literal["working", "waiting", "completed", "failed"]
    message: str
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    handoff_to: str | None = None
    final_action: str | None = None
    final_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    final_output: dict[str, Any] | None = None


class PolicyOutput(BaseModel):
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_level: Literal["low", "medium", "high"]
    issues: list[str] = Field(default_factory=list)
    status_message: str
    ui_events: list[AgentUIEvent] = Field(default_factory=list)


class ConfidenceOutput(BaseModel):
    confidence_score: float = Field(ge=0.0, le=1.0)
    status_message: str
    ui_events: list[AgentUIEvent] = Field(default_factory=list)


class ActionOutput(BaseModel):
    final_action: Literal["APPROVE", "HOLD", "ESCALATE", "REVIEW"]
    final_confidence: float = Field(ge=0.0, le=1.0)
    risk_level: Literal["low", "medium", "high"]
    reason: str
    status_message: str
    requires_human_review: bool
    ui_events: list[AgentUIEvent] = Field(default_factory=list)


class GuardrailOutput(BaseModel):
    validated_action: Literal["APPROVE", "HOLD", "ESCALATE", "REVIEW"]
    adjusted: bool
    adjustment_reason: str
    ui_events: list[AgentUIEvent] = Field(default_factory=list)


class HILOutput(BaseModel):
    review_required: bool
    review_reason: str
    analyst_summary: str
    ui_events: list[AgentUIEvent] = Field(default_factory=list)


def _build_llm() -> ChatOpenAI:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0)


def build_policy_llm() -> ChatOpenAI:
    return _build_llm().with_structured_output(
        PolicyOutput,
        method="function_calling",
    )


def build_confidence_llm() -> ChatOpenAI:
    return _build_llm().with_structured_output(
        ConfidenceOutput,
        method="function_calling",
    )


def build_action_llm() -> ChatOpenAI:
    return _build_llm().with_structured_output(
        ActionOutput,
        method="function_calling",
    )


def build_guardrail_llm() -> ChatOpenAI:
    return _build_llm().with_structured_output(
        GuardrailOutput,
        method="function_calling",
    )


def build_hil_llm() -> ChatOpenAI:
    return _build_llm().with_structured_output(
        HILOutput,
        method="function_calling",
    )