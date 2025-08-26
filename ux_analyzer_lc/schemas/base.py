from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class Quote(BaseModel):
    text: str = Field(..., description="Дословная цитата, >= требуемой длины слов")
    context: Optional[str] = None
    emotion: Optional[str] = None
    source_chunk: Optional[str] = None

class ThemedItem(BaseModel):
    title: str
    description: str
    quotes: List[Quote] = []

class PainNeed(BaseModel):
    label: str
    description: str
    priority: Optional[str] = None  # high/mid/low
    quotes: List[Quote] = []

class EmotionMoment(BaseModel):
    trigger: str
    intensity: Optional[str] = None
    quotes: List[Quote] = []

class Insight(BaseModel):
    statement: str
    rationale: str
    quotes: List[Quote] = []

class BriefAnswer(BaseModel):
    question: str
    answer: str
    evidence_quotes: List[Quote] = []
    confidence: Optional[float] = None
    interviews: List[str] = []

class GoalAssessment(BaseModel):
    goal: str
    status: str  # achieved/partial/not
    rationale: str
    confidence: Optional[float] = None
    gaps: List[str] = []
    required_actions: List[str] = []

class Segment(BaseModel):
    name: str
    criteria: str
    size_hint: Optional[str] = None
    interview_ids: List[str] = []
    key_pains: List[str] = []
    key_needs: List[str] = []
    quotes: List[Quote] = []

class Persona(BaseModel):
    name: str
    segment: Optional[str] = None
    goals: List[str] = []
    blockers: List[str] = []
    channels: List[str] = []
    scenarios: List[str] = []
    quotes: List[Quote] = []

class Recommendation(BaseModel):
    title: str
    category: str  # quick_win/mid/strategic
    rationale: str
    effort: Optional[str] = None
    impact: Optional[str] = None
    risks: List[str] = []
    dependencies: List[str] = []
    success_metrics: List[str] = []

class Findings(BaseModel):
    executive_summary: str
    key_insights: List[Insight]
    risks: List[str] = []
    assumptions: List[str] = []
    recommendations: List[Recommendation] = []
    personas: List[Persona] = []
