from __future__ import annotations
import json, hashlib
from pathlib import Path
from typing import Any
from ..config import SETTINGS

def _hash_key(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update((p or '').encode('utf-8', errors='ignore'))
    return h.hexdigest()

def cache_dir() -> Path:
    p = Path(SETTINGS.cache_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p

def get(key_parts: list[str]) -> Any | None:
    key = _hash_key(*key_parts)
    f = cache_dir() / f"{key}.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding='utf-8'))
        except Exception:
            return None
    return None

def set(key_parts: list[str], value: Any) -> None:
    key = _hash_key(*key_parts)
    f = cache_dir() / f"{key}.json"
    f.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
