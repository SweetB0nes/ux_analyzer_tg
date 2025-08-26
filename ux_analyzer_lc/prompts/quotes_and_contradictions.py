from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Собрать 1–5 коротких дословных цитат и 0–3 противоречия.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"quotes":[{"text":"Где видно итоговую сумму?","context":"оплата","emotion":"растерянность"}],"contradictions":["Сначала говорит, что всё понятно, затем спрашивает про комиссию"]}\n"""
    + """Схема ответа (строго): {"quotes":[{"text":"string","context":"string","emotion":"string"}],"contradictions":["string"]}\n"""
    + "{format_instructions}\n"
    + "ТЕКСТ:\n----\n{transcript_chunk}\n----\n"
    + GUARDRAILS
)
PROMPT = PromptTemplate.from_template(TEMPLATE)
