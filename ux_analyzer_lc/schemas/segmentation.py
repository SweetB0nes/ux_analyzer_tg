from __future__ import annotations
from typing import List, Dict
from pydantic import BaseModel, Field

class Segment(BaseModel):
    name: str = ""
    criteria: str = ""
    size_hint: str = ""
    interview_ids: List[str] = Field(default_factory=list)
    key_pains: List[str] = Field(default_factory=list)
    key_needs: List[str] = Field(default_factory=list)
    quotes: List[Dict] = Field(default_factory=list)  # [{"text": "..."}]

class Segmentation(BaseModel):
    segments: List[Segment] = Field(default_factory=list)