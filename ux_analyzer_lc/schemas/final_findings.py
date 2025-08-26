from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field

class Persona(BaseModel):
    name: str = ""
    segment: str = ""
    goals: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    channels: List[str] = Field(default_factory=list)
    scenarios: List[str] = Field(default_factory=list)
    quotes: List[dict] = Field(default_factory=list)  # [{"text": "..."}]

class Findings(BaseModel):
    executive_summary: str = ""
    key_insights: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)  # краткий список названий
    personas: List[Persona] = Field(default_factory=list)

    # опционально для «Материалов для защиты»
    decision_criteria: List[str] = Field(default_factory=list)