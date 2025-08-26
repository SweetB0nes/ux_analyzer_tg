from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Извлечь боли и потребности с приоритетами.\n"
    + "Мини-пример JSON (пример, не данные из интервью):\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"pains":[{"label":"Неочевидный шаг подтверждения","description":"После карты появляется доп. экран","priority":"high","quotes":[{"text":"Я не ожидал второй шаг"}]}],"needs":[{"label":"Прозрачная стоимость","description":"Видеть итоговую сумму заранее","priority":"mid","quotes":[{"text":"Хочу видеть комиссию до оплаты"}]}]}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последних двойных кавычек в схеме
    + """{"pains":[{"label":"string","description":"string","priority":"high|mid|low","quotes":[{"text":"string"}]}],"needs":[{"label":"string","description":"string","priority":"high|mid|low","quotes":[{"text":"string"}]}]}\n"""
    + "Правила: цитаты >= {min_quote_length} слов.\n"
    + "{format_instructions}\n"
    + "ТЕКСТ:\n----\n{transcript_chunk}\n----\n"
    + GUARDRAILS
)

PROMPT = PromptTemplate.from_template(TEMPLATE)
