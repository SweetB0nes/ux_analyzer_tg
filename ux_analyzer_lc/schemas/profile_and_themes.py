from __future__ import annotations
from pydantic import BaseModel
from typing import List
from .base import ThemedItem, Quote

class ProfileAndThemes(BaseModel):
    respondent_profile: str
    key_themes: List[ThemedItem]
    quotes: List[Quote]
