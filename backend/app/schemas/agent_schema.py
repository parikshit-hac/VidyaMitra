from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AgentOrchestrateRequest(BaseModel):
    goal: str = Field(min_length=5, max_length=500)
    target_role: str = Field(default="", max_length=120)
    constraints: str = Field(default="", max_length=1000)
    include_resources: bool = True
    include_progress: bool = True


class AgentStep(BaseModel):
    step_id: int
    agent: str
    action: str
    action_key: str | None = None
    status: str
    needs_approval: bool = False
    output: dict = Field(default_factory=dict)


class AgentOrchestrateResponse(BaseModel):
    run_id: UUID
    goal: str
    status: str
    plan: list[dict]
    trace: list[AgentStep]
    result: dict
    created_at: datetime | None = None
