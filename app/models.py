from __future__ import annotations
from typing import Any, Optional, Literal
from pydantic import BaseModel, Field


class EmailSnapshot(BaseModel):
    id: str
    subject: str
    sender: str
    sender_domain: str
    timestamp: str
    preview: str
    has_attachments: bool = False
    thread_depth: int = 0
    word_count: int = 0


class Observation(BaseModel):
    step: int
    inbox: list[EmailSnapshot]
    processed_count: int
    pending_count: int
    current_email: Optional[EmailSnapshot] = None
    current_email_body: Optional[str] = None
    task_description: str
    task_id: str
    progress: float
    cumulative_reward: float
    available_actions: list[str]
    context: dict[str, Any] = Field(default_factory=dict)


class Action(BaseModel):
    action_type: Literal["triage", "respond", "escalate", "archive", "flag", "compose", "skip"]
    email_id: str
    category: Optional[Literal["urgent", "normal", "low", "spam", "internal", "external"]] = None
    response_text: Optional[str] = None
    priority_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    reason: Optional[str] = None
    escalate_to: Optional[str] = None


class Reward(BaseModel):
    value: float
    components: dict[str, float] = Field(default_factory=dict)
    explanation: str


class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict[str, Any]


class ResetResponse(BaseModel):
    observation: Observation
    task_id: str


class StateResponse(BaseModel):
    state: dict[str, Any]


class TaskInfo(BaseModel):
    task_id: str
    name: str
    description: str
    difficulty: Literal["easy", "medium", "hard"]
    max_steps: int
    action_schema: dict[str, Any]
