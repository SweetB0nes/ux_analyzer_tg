from __future__ import annotations
from pydantic import BaseModel
from typing import List
from .base import Quote

class BriefLinkage(BaseModel):
    goal_links: List[str]
    question_links: List[str]
    quotes: List[Quote]
