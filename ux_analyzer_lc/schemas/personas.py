from __future__ import annotations
from typing import List, Dict
from pydantic import BaseModel, Field

class Persona(BaseModel):
    name: str = ""
    segment: str = ""
    goals: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    channels: List[str] = Field(default_factory=list)
    scenarios: List[str] = Field(default_factory=list)
    quotes: List[Dict] = Field(default_factory=list)  # [{"text": "..."}]

class Personas(BaseModel):
    personas: List[Persona] = Field(default_factory=list)