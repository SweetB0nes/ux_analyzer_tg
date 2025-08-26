# ux_analyzer_lc/analysis/analyzer.py
from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from typing import Iterable, List, Dict, Any

# --- интервальные цепочки (по каждому интервью) ---
from ux_analyzer_lc.chains.profile_and_themes import build as build_profile_and_themes
from ux_analyzer_lc.chains.pains_and_needs import build as build_pains_and_needs
from ux_analyzer_lc.chains.emotions_and_insights import build as build_emotions_and_insights
from ux_analyzer_lc.chains.quotes_and_contradictions import build as build_quotes_and_contradictions

# --- кросс-цепочки (по агрегатам) ---
from ux_analyzer_lc.chains.business_aspects import build as build_business_aspects
from ux_analyzer_lc.chains.brief_linkage import build as build_brief_linkage
from ux_analyzer_lc.chains.cross_analysis import build as build_cross_analysis
from ux_analyzer_lc.chains.patterns import build as build_patterns
from ux_analyzer_lc.chains.segmentation import build as build_segmentation
from ux_analyzer_lc.chains.personas import build as build_personas

# --- финальные цепочки (по агрегатам) ---
from ux_analyzer_lc.chains.brief_questions import build as build_brief_questions
from ux_analyzer_lc.chains.goal_achievement import build as build_goal_achievement
from ux_analyzer_lc.chains.recommendations import build as build_recommendations
from ux_analyzer_lc.chains.final_findings import build as build_final_findings

log = logging.getLogger(__name__)

MIN_QUOTE_WORDS = 4


@dataclass
class Analyzer:
    brief: Dict[str, Any]

    # ----------------------------- public API -----------------------------
    def run(self, transcripts: Iterable[tuple[str, str]]) -> Dict[str, Any]:
        """
        transcripts: Iterable[(interview_id, text)]
        returns payload dict, готовый для report.html.j2
        """
        interviews_payload = self._per_interview(transcripts)
        aggregates = self._make_aggregates(interviews_payload)
        cross = self._run_cross(aggregates)
        final = self._run_final_sections(aggregates, cross)

        payload = {
            "interviews": interviews_payload,
            "cross": {
                "aggregates": aggregates,
                "cross": cross,
            },
            "final": final,
        }
        return payload

    # ----------------------- per-interview pass --------------------------
    def _per_interview(self, transcripts: Iterable[tuple[str, str]]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []

        brief_ctx = self._brief_context_text()

        # билдеры
        chain_profile = build_profile_and_themes()
        chain_pain = build_pains_and_needs()
        chain_emo = build_emotions_and_insights()
        chain_quotes = build_quotes_and_contradictions()

        for int_id, text in transcripts:
            txt = (text or "").strip()
            if not txt:
                log.warning("Interview '%s' has empty text. Skipping LLM calls.", int_id)
                items.append({
                    "interview_id": int_id,
                    "summaries": {},
                    "sentiment": 0.0,
                })
                continue

            # --- вызовы цепочек ---
            try:
                s_profile = chain_profile.invoke({
                    "brief_context": brief_ctx,
                    "transcript_chunk": txt,
                    "min_quote_length": str(MIN_QUOTE_WORDS),
                })
            except Exception as e:
                log.error("profile_and_themes failed for %s: %s", int_id, e)
                s_profile = None

            try:
                s_pains = chain_pain.invoke({
                    "brief_context": brief_ctx,
                    "transcript_chunk": txt,
                    "min_quote_length": str(MIN_QUOTE_WORDS),
                })
            except Exception as e:
                log.error("pains_and_needs failed for %s: %s", int_id, e)
                s_pains = None

            try:
                s_emo = chain_emo.invoke({
                    "brief_context": brief_ctx,
                    "transcript_chunk": txt,
                    "min_quote_length": str(MIN_QUOTE_WORDS),
                })
            except Exception as e:
                log.error("emotions_and_insights failed for %s: %s", int_id, e)
                s_emo = None

            try:
                s_quotes = chain_quotes.invoke({
                    "brief_context": brief_ctx,
                    "transcript_chunk": txt,
                })
            except Exception as e:
                log.error("quotes_and_contradictions failed for %s: %s", int_id, e)
                s_quotes = None

            # --- сбор summaries для интервью ---
            summaries: Dict[str, Any] = {}

            if s_profile and getattr(s_profile, "model_dump", None):
                pd = s_profile.model_dump()
                summaries["profile_and_themes"] = pd
                # плоские поля дублируем, чтобы рендер проще был
                if pd.get("key_themes"):
                    summaries["themes"] = pd["key_themes"]
                if pd.get("quotes"):
                    summaries.setdefault("quotes", []).extend(pd["quotes"])

            if s_pains and getattr(s_pains, "model_dump", None):
                d = s_pains.model_dump()
                if d.get("pains"):
                    summaries["pains"] = d["pains"]
                if d.get("needs"):
                    summaries["needs"] = d["needs"]

            if s_emo and getattr(s_emo, "model_dump", None):
                d = s_emo.model_dump()
                if d.get("emotions"):
                    summaries["emotions"] = d["emotions"]
                if d.get("insights"):
                    summaries["insights"] = d["insights"]

            if s_quotes and getattr(s_quotes, "model_dump", None):
                d = s_quotes.model_dump()
                if d.get("quotes"):
                    summaries.setdefault("quotes", []).extend(d["quotes"])
                if d.get("contradictions"):
                    summaries["contradictions"] = d["contradictions"]

            items.append({
                "interview_id": int_id,
                "summaries": summaries,
                "sentiment": 0.0,  # здесь можно прикрутить простую метрику тона
            })

        return items

    # ----------------------- aggregates over all -------------------------
    def _make_aggregates(self, interviews_payload: List[Dict[str, Any]]) -> Dict[str, Any]:
        agg: Dict[str, Any] = {
            "profiles": [],
            "themes": [],
            "pains": [],
            "needs": [],
            "emotions": [],
            "insights": [],
            "quotes": [],
            "contradictions": [],
            "opportunities": [],
            "metric_links": [],
            "goal_links": [],
            "question_links": [],
            "sentiments": [],
        }

        for iv in interviews_payload:
            sums = iv.get("summaries") or {}
            pat = (sums.get("profile_and_themes") or {})

            if pat.get("respondent_profile"):
                agg["profiles"].append(pat["respondent_profile"])

            for k in ["themes", "pains", "needs", "emotions", "insights", "quotes", "contradictions"]:
                v = sums.get(k)
                if v:
                    agg[k].extend(v)

            if isinstance(iv.get("sentiment"), (int, float)):
                agg["sentiments"].append(iv["sentiment"])

        return agg

    # ------------------------ cross chains on agg ------------------------
    def _run_cross(self, aggregates: Dict[str, Any]) -> Dict[str, Any]:
        brief_ctx = self._brief_context_text()
        agg_str = json.dumps(aggregates, ensure_ascii=False)

        # билдеры
        ch_business = build_business_aspects()
        ch_brief = build_brief_linkage()
        ch_cross = build_cross_analysis()
        ch_patterns = build_patterns()
        ch_segm = build_segmentation()
        ch_persona = build_personas()

        # invoke (ловим ошибки по каждой цепочке отдельно, чтобы не падал весь анализ)
        try:
            business = ch_business.invoke({"brief_context": brief_ctx, "transcript_chunk": agg_str})
        except Exception as e:
            log.error("business_aspects failed: %s", e)
            business = None

        try:
            brief_lnk = ch_brief.invoke({"brief_context": brief_ctx, "transcript_chunk": agg_str})
        except Exception as e:
            log.error("brief_linkage failed: %s", e)
            brief_lnk = None

        try:
            cross = ch_cross.invoke({"brief_context": brief_ctx, "aggregates": agg_str})
        except Exception as e:
            log.error("cross_analysis failed: %s", e)
            cross = None

        try:
            patterns = ch_patterns.invoke({"brief_context": brief_ctx, "aggregates": agg_str})
        except Exception as e:
            log.error("patterns failed: %s", e)
            patterns = None

        try:
            segments = ch_segm.invoke({"brief_context": brief_ctx, "aggregates": agg_str})
        except Exception as e:
            log.error("segmentation failed: %s", e)
            segments = None

        try:
            personas = ch_persona.invoke({"brief_context": brief_ctx, "aggregates": agg_str})
        except Exception as e:
            log.error("personas failed: %s", e)
            personas = None

        # записываем бизнес-аспекты и линковки назад в aggregates (их оттуда берёт шаблон)
        if business and getattr(business, "model_dump", None):
            bd = business.model_dump()
            if bd.get("opportunities"):
                aggregates["opportunities"] = bd["opportunities"]
            if bd.get("metric_links"):
                aggregates["metric_links"] = bd["metric_links"]

        if brief_lnk and getattr(brief_lnk, "model_dump", None):
            bl = brief_lnk.model_dump()
            if bl.get("goal_links"):
                aggregates["goal_links"] = bl["goal_links"]
            if bl.get("question_links"):
                aggregates["question_links"] = bl["question_links"]

        # формируем cross-блок для отчёта
        out = {
            "cross_analysis": getattr(cross, "model_dump", lambda: {})(),
            "patterns": getattr(patterns, "model_dump", lambda: {})(),
            "segmentation": getattr(segments, "model_dump", lambda: {})(),
            "personas": getattr(personas, "model_dump", lambda: {})(),
        }
        return out

    # ------------------------ final chains on agg ------------------------
    def _run_final_sections(self, aggregates: Dict[str, Any], cross: Dict[str, Any]) -> Dict[str, Any]:
        brief_ctx = self._brief_context_text()
        agg_str = json.dumps(aggregates, ensure_ascii=False)

        ch_answers = build_brief_questions()
        ch_goals = build_goal_achievement()
        ch_recs = build_recommendations()
        ch_final = build_final_findings()

        try:
            answers = ch_answers.invoke({"brief_context": brief_ctx, "aggregates": agg_str})
        except Exception as e:
            log.error("brief_questions failed: %s", e)
            answers = None

        try:
            goals = ch_goals.invoke({"brief_context": brief_ctx, "aggregates": agg_str})
        except Exception as e:
            log.error("goal_achievement failed: %s", e)
            goals = None

        try:
            recs = ch_recs.invoke({"brief_context": brief_ctx, "aggregates": agg_str})
        except Exception as e:
            log.error("recommendations failed: %s", e)
            recs = None

        try:
            final = ch_final.invoke({"brief_context": brief_ctx, "aggregates": agg_str})
        except Exception as e:
            log.error("final_findings failed: %s", e)
            final = None

        final_block = {
            "brief_answers": getattr(answers, "model_dump", lambda: {})(),
            "goal_achievement": getattr(goals, "model_dump", lambda: {})(),
            "recommendations": getattr(recs, "model_dump", lambda: {})(),
            "final_findings": getattr(final, "model_dump", lambda: {})(),
            "defense_materials": self._mk_defense_block(
                aggregates=aggregates,
                cross=cross,
                recs=recs,
                final=final,
            ),
        }
        return final_block

    # ----------------- compose "defense materials" -----------------------
    def _mk_defense_block(self, aggregates, cross, recs, final) -> Dict[str, Any]:
        def _dump(x):
            return getattr(x, "model_dump", lambda: {})()

        f = _dump(final)
        r = _dump(recs)

        key_findings = f.get("key_insights") or []
        critical_risks = (cross.get("cross_analysis") or {}).get("risks") or []
        assumptions = f.get("assumptions") or []
        # из рекомендаций можно вынести Next Steps / метрики успеха
        next_steps = r.get("next_steps") or []
        decision_criteria = f.get("decision_criteria") or []
        tracking_metrics = r.get("success_metrics") or []

        return {
            "key_findings": key_findings,
            "critical_risks": critical_risks,
            "assumptions": assumptions,
            "next_steps": next_steps,
            "decision_criteria": decision_criteria,
            "tracking_metrics": tracking_metrics,
        }

    # ------------------------ brief → context text -----------------------
    def _brief_context_text(self) -> str:
        """Компактный текстовый контекст брифа: title/company/goals/questions/..."""
        if not self.brief:
            return ""
        p = self.brief.get("project") or {}
        parts = []
        if p.get("title"):
            parts.append(f"Проект: {p.get('title')}")
        if p.get("company"):
            parts.append(f"Компания: {p.get('company')}")
        if self.brief.get("goals"):
            parts.append("Цели: " + "; ".join(self.brief["goals"]))
        if self.brief.get("questions"):
            parts.append("Вопросы: " + "; ".join(self.brief["questions"]))
        if self.brief.get("audience"):
            parts.append("Аудитория: " + "; ".join(self.brief["audience"]))
        if self.brief.get("success_metrics"):
            parts.append("Метрики успеха: " + "; ".join(self.brief["success_metrics"]))
        return " | ".join(parts)
