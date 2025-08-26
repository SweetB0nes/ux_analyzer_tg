from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field

class Patterns(BaseModel):
    behavioral_patterns: List[str] = Field(default_factory=list)