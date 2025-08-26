from __future__ import annotations
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

def _to_bool(x: str | None, default: bool = True) -> bool:
    if x is None:
        return default
    return str(x).strip().lower() in ("1", "true", "yes", "y", "on")

@dataclass
class Settings:
    model_name: str = os.getenv("MODEL_NAME", "gemini-1.5-pro")
    temperature: float = float(os.getenv("TEMPERATURE", "0.0"))
    max_output_tokens: int = int(os.getenv("MAX_OUTPUT_TOKENS", "8192"))
    window_size: int = int(os.getenv("WINDOW_SIZE", "10000"))
    overlap: int = int(os.getenv("OVERLAP", "2000"))
    use_speaker_splitting: bool = _to_bool(os.getenv("USE_SPEAKER_SPLITTING", "true"))
    require_exact_quotes: bool = _to_bool(os.getenv("REQUIRE_EXACT_QUOTES", "true"))
    min_quote_length: int = int(os.getenv("MIN_QUOTE_LENGTH", "60"))
    output_dir: str = os.getenv("OUTPUT_DIR", "./outputs")
    cache_dir: str = os.getenv("CACHE_DIR", "./.cache")

    # keys
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")
    gigachat_credentials: str | None = os.getenv("GIGACHAT_CREDENTIALS")
    gigachat_scope: str | None = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    gigachat_verify_ssl: bool = _to_bool(os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false"))

SETTINGS = Settings()
