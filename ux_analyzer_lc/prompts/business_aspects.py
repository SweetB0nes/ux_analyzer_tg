from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Бизнес-связи и возможности.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"opportunities":["Показывать итоговую стоимость на первом экране"],"metric_links":["CR онбординга","NPS"],"quotes":[{"text":"Хочу видеть комиссию сразу"}]}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последней двойной кавычки в схеме
    + """{"opportunities":["string"],"metric_links":["string"],"quotes":[{"text":"string"}]}\n"""
    + "{format_instructions}\n"
    + "ТЕКСТ:\n----\n{transcript_chunk}\n----\n"
    + GUARDRAILS
)

PROMPT = PromptTemplate.from_template(TEMPLATE)
