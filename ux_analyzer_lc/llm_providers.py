from __future__ import annotations
import os
import time
import ssl
from typing import List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatResult
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_gigachat.chat_models import GigaChat

try:
    import httpx  # для типов ошибок сети
except Exception:
    httpx = None


class ProviderError(RuntimeError):
    pass


# ---------- builders ----------

def _build_google() -> BaseChatModel:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ProviderError("GOOGLE_API_KEY is not set")
    model = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    return ChatGoogleGenerativeAI(model=model, api_key=api_key, temperature=temperature)


def _build_gigachat() -> BaseChatModel:
    creds = os.getenv("GIGACHAT_CREDENTIALS")
    if not creds:
        raise ProviderError("GIGACHAT_CREDENTIALS is not set")
    verify = os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() not in ("false", "0", "no")
    scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    return GigaChat(
        credentials=creds,
        verify_ssl_certs=verify,
        scope=scope,
        temperature=temperature,
    )


# ---------- resilient wrapper (primary with retry -> fallback) ----------

RETRYABLE_MSG_PARTS = (
    "timed out", "timeout", "handshake", "CERTIFICATE", "429", "quota", "TooManyRequests",
    "temporarily unavailable", "Service Unavailable"
)

def _is_retryable_error(e: Exception) -> bool:
    if isinstance(e, ssl.SSLError):
        return True
    if httpx is not None and isinstance(e, (httpx.ConnectError, httpx.ReadTimeout)):
        return True
    s = str(e)
    return any(part.lower() in s.lower() for part in RETRYABLE_MSG_PARTS)


class ResilientDualModel(BaseChatModel):
    """
    Пробует primary (Gemini) до max_retries раз с экспоненциальным бэкоффом.
    Если не вышло — переключается на fallback (GigaChat).
    """
    # позволяем произвольные типы и дополнительные поля (pydantic v2)
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    def __init__(self, primary: BaseChatModel, fallback: BaseChatModel,
                 max_retries: int = 5, base_backoff: float = 1.0):
        super().__init__()
        # ВАЖНО: не обычное присваивание, а через object.__setattr__
        object.__setattr__(self, "primary", primary)
        object.__setattr__(self, "fallback", fallback)
        object.__setattr__(self, "max_retries", max_retries)
        object.__setattr__(self, "base_backoff", base_backoff)

    @property
    def _llm_type(self) -> str:
        return "resilient-dual(gemini->gigachat)"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager=None,
        **kwargs,
    ) -> ChatResult:
        last: Exception | None = None
        for i in range(self.max_retries):
            try:
                return self.primary._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
            except Exception as e:
                last = e
                # функция _is_retryable_error у тебя уже есть выше
                if not _is_retryable_error(e):
                    break
                time.sleep(self.base_backoff * (2 ** i))

        # fallback
        try:
            return self.fallback._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        except Exception as e2:
            raise ProviderError(
                f"Primary(Gemini) failed after retries ({last}); fallback(GigaChat) failed: {e2}"
            ) from e2


# ---------- public factory ----------

class LLMFactory:
    @staticmethod
    def make_chat_model() -> BaseChatModel:
        # Явный форс, если нужен: LLM_PREFERRED={GEMINI|GIGACHAT|AUTO}
        preferred = (os.getenv("LLM_PREFERRED") or "AUTO").upper()

        if preferred == "GIGACHAT":
            return _build_gigachat()
        if preferred == "GEMINI":
            return _build_google()

        # AUTO: primary=Gemini -> fallback=GigaChat
        # Если Gemini недоступен по ключу, сразу возвращаем GigaChat.
        try:
            primary = _build_google()
        except Exception:
            # нет ключа/конфиг сломан
            return _build_gigachat()

        # Если нет GigaChat — используем только Gemini (без обёртки)
        try:
            fallback = _build_gigachat()
        except Exception:
            return primary

        max_retries = int(os.getenv("LLM_PRIMARY_MAX_RETRIES", "5"))
        base_backoff = float(os.getenv("LLM_PRIMARY_BACKOFF", "1.0"))
        return ResilientDualModel(primary, fallback, max_retries=max_retries, base_backoff=base_backoff)
