from __future__ import annotations
from typing import Dict, Any
from .base import build_chain
from ..config import SETTINGS

from ..prompts.profile_and_themes import PROMPT as PROMPT_PROFILE
from ..prompts.pains_and_needs import PROMPT as PROMPT_PN
from ..prompts.emotions_and_insights import PROMPT as PROMPT_EI
from ..prompts.quotes_and_contradictions import PROMPT as PROMPT_QC
from ..prompts.business_aspects import PROMPT as PROMPT_BA
from ..prompts.brief_linkage import PROMPT as PROMPT_BL
from ..prompts.cross_analysis import PROMPT as PROMPT_CROSS
from ..prompts.patterns import PROMPT as PROMPT_PAT
from ..prompts.segmentation import PROMPT as PROMPT_SEG
from ..prompts.personas import PROMPT as PROMPT_PER
from ..prompts.final_findings import PROMPT as PROMPT_FIN
from ..prompts.recommendations import PROMPT as PROMPT_REC
from ..prompts.defense_materials import PROMPT as PROMPT_DEF
from ..prompts.brief_questions import PROMPT as PROMPT_BQ
from ..prompts.goal_achievement import PROMPT as PROMPT_GA

from ..schemas.profile_and_themes import ProfileAndThemes
from ..schemas.pains_and_needs import PainsAndNeeds
from ..schemas.emotions_and_insights import EmotionsAndInsights
from ..schemas.quotes_and_contradictions import QuotesAndContradictions
from ..schemas.business_aspects import BusinessAspects
from ..schemas.brief_linkage import BriefLinkage
from ..schemas.cross_analysis import CrossAnalysis
from ..schemas.patterns import Patterns
from ..schemas.segmentation import Segmentation
from ..schemas.personas import Personas
from ..schemas.final_findings import FinalFindings
from ..schemas.recommendations import Recommendations
from ..schemas.defense_materials import DefenseMaterials
from ..schemas.brief_questions import BriefQuestions
from ..schemas.goal_achievement import GoalAchievement

def _fmt(brief: dict) -> Dict[str, Any]:
    goals = "; ".join(brief.get("goals", []))
    questions = "; ".join(brief.get("questions", []))
    audience = "; ".join(brief.get("audience", []))
    metrics = "; ".join(brief.get("success_metrics", []))
    constraints = "; ".join(brief.get("constraints", []))
    brief_context = f"""Вы — аналитик UX. Работайте строго по тексту.
Цели: {goals}
Вопросы: {questions}
ЦА: {audience}
Метрики успеха: {metrics}
Ограничения: {constraints}
Требование к цитатам: >= {SETTINGS.min_quote_length} слов, дословно."""
    return {"brief_context": brief_context, "min_quote_length": SETTINGS.min_quote_length}

def format_brief_context(brief: dict) -> str:
    goals = "; ".join(brief.get("goals", []))
    questions = "; ".join(brief.get("questions", []))
    audience = "; ".join(brief.get("audience", []))
    metrics = "; ".join(brief.get("success_metrics", []))
    constraints = "; ".join(brief.get("constraints", []))
    raw = brief.get("raw_brief", "")
    raw_block = f"\nДоп. текст брифа:\n{raw}\n" if raw else ""
    return f"""
Вы — аналитик UX. Работайте строго по тексту. 
Цели: {goals}
Вопросы: {questions}
ЦА: {audience}
Метрики успеха: {metrics}
Ограничения: {constraints}{raw_block}
Требования к цитатам: >= {SETTINGS.min_quote_length} слов, дословно.
""".strip()

def chain_profile_and_themes(brief: dict): return build_chain(PROMPT_PROFILE, ProfileAndThemes, _fmt(brief))
def chain_pains_and_needs(brief: dict): return build_chain(PROMPT_PN, PainsAndNeeds, _fmt(brief))
def chain_emotions_and_insights(brief: dict): return build_chain(PROMPT_EI, EmotionsAndInsights, _fmt(brief))
def chain_quotes_and_contradictions(brief: dict): return build_chain(PROMPT_QC, QuotesAndContradictions, _fmt(brief))
def chain_business_aspects(brief: dict): return build_chain(PROMPT_BA, BusinessAspects, _fmt(brief))
def chain_brief_linkage(brief: dict): return build_chain(PROMPT_BL, BriefLinkage, _fmt(brief))
def chain_cross_analysis(brief: dict): return build_chain(PROMPT_CROSS, CrossAnalysis, _fmt(brief))
def chain_patterns(brief: dict): return build_chain(PROMPT_PAT, Patterns, _fmt(brief))
def chain_segmentation(brief: dict): return build_chain(PROMPT_SEG, Segmentation, _fmt(brief))
def chain_personas(brief: dict): return build_chain(PROMPT_PER, Personas, _fmt(brief))
def chain_final_findings(brief: dict): return build_chain(PROMPT_FIN, FinalFindings, _fmt(brief))
def chain_recommendations(brief: dict): return build_chain(PROMPT_REC, Recommendations, _fmt(brief))
def chain_defense_materials(brief: dict): return build_chain(PROMPT_DEF, DefenseMaterials, _fmt(brief))
def chain_brief_questions(brief: dict): return build_chain(PROMPT_BQ, BriefQuestions, _fmt(brief))
def chain_goal_achievement(brief: dict): return build_chain(PROMPT_GA, GoalAchievement, _fmt(brief))
