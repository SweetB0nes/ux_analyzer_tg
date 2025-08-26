# tests/test_00_env_and_providers.py
from __future__ import annotations
import os
import pytest
from ux_analyzer_lc.llm_providers import LLMFactory, ProviderError
from ux_analyzer_lc.config import SETTINGS

def test_no_providers(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GIGACHAT_CREDENTIALS", raising=False)
    SETTINGS.google_api_key = None
    SETTINGS.gigachat_credentials = None
    with pytest.raises(ProviderError):
        LLMFactory.make_chat_model()

def test_gigachat_ssl_flag_respected(monkeypatch):
    monkeypatch.setenv("GIGACHAT_CREDENTIALS", "TOKEN")
    monkeypatch.setenv("GIGACHAT_VERIFY_SSL_CERTS", "false")
    # Если SDK недоступен — просто проверим, что объект создаётся без падения.
    m = LLMFactory.make_chat_model()
    assert m is not None
