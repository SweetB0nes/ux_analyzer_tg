from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class BriefAnswer(BaseModel):
    question: str = ""
    answer: str = ""
    evidence_quotes: List[dict] = Field(default_factory=list)  # [{"text": "..."}]
    confidence: float = 0.0
    interviews: List[str] = Field(default_factory=list)

class BriefQuestions(BaseModel):
    answers: List[BriefAnswer] = Field(default_factory=list)