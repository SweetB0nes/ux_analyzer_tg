# tests/_fakes.py
from __future__ import annotations
from typing import Any, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

class FakeChatModel(BaseChatModel):
    """Возвращает заранее заданный JSON-пейлоад строкой."""
    model_config = {"extra": "allow"}

    def __init__(self, payload: str):
        super().__init__()
        object.__setattr__(self, "_payload", payload)

    @property
    def _llm_type(self) -> str:
        return "fake"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self._payload))])

def minimal_payload_for(schema_name: str) -> str:
    """Даёт минимально валидный JSON для разных схем.
    Подстрой, если у тебя поля отличаются.
    """
    base: Dict[str, Any] = {
        "profile_and_themes": '{"key_themes":[{"title":"Найденная тема","description":"Описание"}]}',
        "pains_and_needs": '{"pains":[{"title":"Боль","details":"..." }],"needs":[{"title":"Нужда","details":"..."}]}',
        "emotions_and_insights": '{"emotions":["frustration"],"insights":[{"title":"Инсайт","rationale":"..."}]}',
        "quotes_and_contradictions": '{"quotes":[{"text":"цитата","who":"user"}],"contradictions":[]}',
        "business_aspects": '{"opportunities":[{"title":"Шанс","impact":"med"}],"metric_links":[]}',
        "brief_linkage": '{"goal_links":[],"question_links":[]}',
        "cross_aggregates": '{"themes":[{"title":"Тема cross"}],"insights":[{"title":"Инсайт cross"}]}',
        "final": '{"final_findings":[{"title":"Вывод"}],"recommendations":[{"title":"Реком","actions":["A"]}]}',
    }
    return base.get(schema_name, '{"ok": true}')
