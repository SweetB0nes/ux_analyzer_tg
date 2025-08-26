from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from typing import Literal

StatusT = Literal["achieved", "partial", "not"]

class GoalEntry(BaseModel):
    goal: str = ""
    status: StatusT = "partial"
    rationale: str = ""
    confidence: float = 0.0
    gaps: List[str] = Field(default_factory=list)
    required_actions: List[str] = Field(default_factory=list)

class GoalAchievement(BaseModel):
    goals: List[GoalEntry] = Field(default_factory=list)