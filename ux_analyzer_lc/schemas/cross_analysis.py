from __future__ import annotations
from typing import Dict, List, Any
from pydantic import BaseModel, Field

class CrossAnalysis(BaseModel):
    # например: частоты тем, риски, сравнительные срезы и т.д.
    frequencies: Dict[str, int] = Field(default_factory=dict)
    risks: List[str] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)
    # на всякий случай, чтобы не падать, если промпт вернёт кастомные ключи
    extra: Dict[str, Any] = Field(default_factory=dict)