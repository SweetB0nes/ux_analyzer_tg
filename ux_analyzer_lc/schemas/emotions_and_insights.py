from __future__ import annotations
from pydantic import BaseModel
from typing import List
from .base import EmotionMoment, Insight

class EmotionsAndInsights(BaseModel):
    emotions: List[EmotionMoment]
    insights: List[Insight]
