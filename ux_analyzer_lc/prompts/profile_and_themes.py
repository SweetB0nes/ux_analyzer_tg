from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Извлечь краткий профиль респондента и ключевые темы (title + description) с 1–2 точными цитатами.\n"
    + "Мини-пример JSON:\n"
    + """{"respondent_profile":"Новый пользователь, платит с телефона","key_themes":[{"title":"Непрозрачная стоимость","description":"Не видит итоговую сумму заранее","quotes":[{"text":"Я не понял, сколько спишут","context":"оплата","emotion":"растерянность"}]}],"quotes":[{"text":"Где видно итого?","context":"оплата","emotion":"напряжение"}]}\n"""
    + """Схема ответа (строго):\n"""
    + """{"respondent_profile":"string","key_themes":[{"title":"string","description":"string","quotes":[{"text":"string","context":"string","emotion":"string"}]}],"quotes":[{"text":"string","context":"string","emotion":"string"}]}\n"""
    + "Правила: цитаты только дословные; каждая цитата ≥ {min_quote_length} слов.\n"
    + "{format_instructions}\n"
    + "ТЕКСТ:\n----\n{transcript_chunk}\n----\n"
    + GUARDRAILS
)
PROMPT = PromptTemplate.from_template(TEMPLATE)
