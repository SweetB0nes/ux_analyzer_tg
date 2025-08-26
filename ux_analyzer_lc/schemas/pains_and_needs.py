from __future__ import annotations
from pydantic import BaseModel
from typing import List
from .base import PainNeed

class PainsAndNeeds(BaseModel):
    pains: List[PainNeed]
    needs: List[PainNeed]
