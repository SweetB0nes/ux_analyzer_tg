from __future__ import annotations
from pathlib import Path
from _fakes import FakeChatModel
from ux_analyzer_lc.analysis.analyzer import Analyzer
from ux_analyzer_lc.report.generator import save_all

SUPERSET_JSON = """
{
  "key_themes": [{"title":"Тема1","description":"desc"}],
  "pains": [{"title":"Боль1","details":"..."}],
  "needs": [{"title":"Нужда1","details":"..."}],
  "emotions": ["frustration"],
  "insights": [{"title":"Инсайт1","rationale":"..."}],
  "quotes": [{"text":"Очень неудобно оплачивать","who":"user"}],
  "contradictions": [],
  "opportunities": [{"title":"Упростить оплату","impact":"med"}],
  "metric_links": [],
  "goal_links": [],
  "question_links": []
}
"""

def test_analyzer_e2e_fake_llm(tmp_path, monkeypatch):
    from ux_analyzer_lc import llm_providers
    # Все цепочки получат один и тот же валидный JSON-суперсет
    monkeypatch.setattr(llm_providers.LLMFactory, "make_chat_model", lambda: FakeChatModel(SUPERSET_JSON))

    transcripts = [("int1", "Пользователь: не понял где оплата. Интервьюер: что ещё?")]
    brief = {"project": {"title": "Demo", "company": "Acme"}}
    analyzer = Analyzer(brief)
    payload = analyzer.run(transcripts)

    cross = payload.get("cross", {}).get("aggregates", {})
    final = payload.get("final", {})
    assert (cross.get("themes") or cross.get("insights") or final.get("recommendations")), "После анализа всё ещё пусто"

    paths = save_all(payload, "Acme", "UX Lab", "UX Report")
    html = paths.get("html")
    assert html and Path(html).exists()
