# tests/test_30_chains_and_parser.py
from __future__ import annotations
import pytest
from _fakes import FakeChatModel, minimal_payload_for

def patch_factory(monkeypatch, payload: str):
    from ux_analyzer_lc import llm_providers
    monkeypatch.setattr(llm_providers.LLMFactory, "make_chat_model", lambda: FakeChatModel(payload))

@pytest.mark.parametrize("schema_name,chain_builder_path", [
    ("profile_and_themes", "ux_analyzer_lc.chains.profile_and_themes.build"),
    ("pains_and_needs", "ux_analyzer_lc.chains.pains_and_needs.build"),
    ("emotions_and_insights", "ux_analyzer_lc.chains.emotions_and_insights.build"),
    ("quotes_and_contradictions", "ux_analyzer_lc.chains.quotes_and_contradictions.build"),
    ("business_aspects", "ux_analyzer_lc.chains.business_aspects.build"),
    ("brief_linkage", "ux_analyzer_lc.chains.brief_linkage.build"),
])
def test_each_chain_parses(monkeypatch, schema_name, chain_builder_path):
    payload = minimal_payload_for(schema_name)
    patch_factory(monkeypatch, payload)
    # динамический импорт билдера
    module_path, func_name = chain_builder_path.rsplit(".", 1)
    mod = __import__(module_path, fromlist=[func_name])
    build = getattr(mod, func_name)
    chain = build()         # без параметров или с дефолтным brief_context
    out = chain({"transcript_chunk": "user text", "brief_context": ""})
    assert out is not None
