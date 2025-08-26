from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Эмоции и инсайты.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"emotions":[{"trigger":"Непрозрачная цена","intensity":"сильная","quotes":[{"text":"Я не понял, сколько спишут"}]}],"insights":[{"statement":"Не хватает ранней видимости цены","rationale":"Понижение неопределенности снижает отказы","quotes":[{"text":"Хочу видеть итоговую сумму заранее"}]}]}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последних двойных кавычек в схеме
    + """{"emotions":[{"trigger":"string","intensity":"string","quotes":[{"text":"string"}]}],"insights":[{"statement":"string","rationale":"string","quotes":[{"text":"string"}]}]}\n"""
    + "Правила: цитаты >= {min_quote_length} слов.\n"
    + "{format_instructions}\n"
    + "ТЕКСТ:\n----\n{transcript_chunk}\n----\n"
    + GUARDRAILS
)

PROMPT = PromptTemplate.from_template(TEMPLATE)
