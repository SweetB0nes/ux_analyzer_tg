from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field

CategoryT = Literal["quick_win", "mid", "strategic"]

class Recommendation(BaseModel):
    title: str = ""
    category: CategoryT = "mid"
    rationale: str = ""
    effort: str = ""
    impact: str = ""
    risks: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)

class Recommendations(BaseModel):
    recommendations: List[Recommendation] = Field(default_factory=list)
    # опционально: агрегаты для «Материалов для защиты»
    next_steps: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)