from __future__ import annotations
from pydantic import BaseModel
from typing import List

class DefenseMaterials(BaseModel):
    key_findings: List[str]
    critical_risks: List[str]
    assumptions: List[str]
    next_steps: List[str]
    decision_criteria: List[str]
    tracking_metrics: List[str]
