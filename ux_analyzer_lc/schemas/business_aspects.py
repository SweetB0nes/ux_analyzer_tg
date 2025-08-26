from __future__ import annotations
from pydantic import BaseModel
from typing import List
from .base import Quote

class BusinessAspects(BaseModel):
    opportunities: List[str]
    metric_links: List[str]
    quotes: List[Quote]
