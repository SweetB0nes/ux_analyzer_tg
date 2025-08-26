from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Tuple, Dict, Any
import re
import yaml

# -------- helpers --------

def _normalize_inline_yaml(text: str) -> str:
    # ставим пробел после двоеточия, если дальше сразу идёт символ (слово, {, [, кавычка и т.п.)
    # примеры: title:A -> title: A, company:B -> company: B, goals:[g1] -> goals: [g1]
    text = re.sub(r":(?=\S)", ": ", text)
    # ставим пробел после запятой, если его нет
    text = re.sub(r",(?=\S)", ", ", text)
    return text

def _yaml_safe_load(text: str) -> Dict[str, Any]:
    # попытка №1 — как есть
    try:
        data = yaml.safe_load(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    # попытка №2 — после нормализации пробелов
    try:
        text2 = _normalize_inline_yaml(text)
        data = yaml.safe_load(text2)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    # попытка №3 — «грубый» разбор конкретных инлайн-кейсов (project:{title:A,...})
    out: Dict[str, Any] = {}
    try:
        # project.title
        m = re.search(r"project\s*:\s*\{[^}]*title\s*:\s*([^,\}\s]+)", text, flags=re.I)
        if m:
            out.setdefault("project", {})["title"] = m.group(1).strip().strip('"\'')
        # project.company
        m = re.search(r"project\s*:\s*\{[^}]*company\s*:\s*([^,\}\s]+)", text, flags=re.I)
        if m:
            out.setdefault("project", {})["company"] = m.group(1).strip().strip('"\'')
        # goals:[g1, g2]
        m = re.search(r"goals\s*:\s*\[([^\]]+)\]", text, flags=re.I)
        if m:
            goals = [g.strip().strip('"\'') for g in m.group(1).split(",") if g.strip()]
            if goals:
                out["goals"] = goals
    except Exception:
        pass
    return out

def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def _read_txt_or_docx(p: Path) -> str:
    suf = p.suffix.lower()
    if suf in (".txt", ".md"):
        return p.read_text(encoding="utf-8", errors="ignore")
    if suf == ".docx":
        try:
            from docx import Document
        except Exception:
            return ""
        try:
            d = Document(str(p))
            return "\n".join(par.text for par in d.paragraphs)
        except Exception:
            return ""
    return ""

# -------- public API --------

def load_transcripts(folder: str) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    for p in sorted(Path(folder).glob("*")):
        if p.suffix.lower() not in (".txt", ".md", ".docx"):
            continue
        text = _read_txt_or_docx(p)
        if text.strip():
            items.append((p.stem, text))
    return items

def load_brief_any(paths: Iterable[Path]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    raw_chunks: List[str] = []
    for p in paths:
        suf = p.suffix.lower()
        if suf in (".yaml", ".yml"):
            ytxt = p.read_text(encoding="utf-8", errors="ignore")
            y = _yaml_safe_load(ytxt)
            merged = _deep_merge(merged, y)
            raw_chunks.append(ytxt)
        elif suf in (".txt", ".md", ".docx"):
            t = _read_txt_or_docx(p)
            raw_chunks.append(t)
        else:
            continue
    # defaults
    merged.setdefault("project", {})
    merged["project"].setdefault("title", "")
    merged["project"].setdefault("company", "")
    merged.setdefault("goals", [])
    merged["raw_brief"] = "\n\n".join(ch for ch in raw_chunks if ch.strip())
    return merged
