from __future__ import annotations
from pydantic import BaseModel
from typing import List
from .base import Quote

class QuotesAndContradictions(BaseModel):
    quotes: List[Quote]
    contradictions: List[str]
