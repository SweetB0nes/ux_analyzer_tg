# tests/test_50_live_smoke_optional.py
from __future__ import annotations
import os
import pytest
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from ux_analyzer_lc.llm_providers import LLMFactory

@pytest.mark.skipif(
    not (os.getenv("GOOGLE_API_KEY") or os.getenv("GIGACHAT_CREDENTIALS")),
    reason="Нет ключей для live-smoke"
)
def test_live_provider_minimal_json():
    class P(BaseModel):
        ok: bool
    parser = PydanticOutputParser(pydantic_object=P)
    prompt = PromptTemplate.from_template("{format_instructions}\nОтветь JSON с ok=true")
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    llm = LLMFactory.make_chat_model()
    raw = (prompt | llm).invoke({})
    data = parser.parse(getattr(raw, "content", raw))
    assert data.ok is True
