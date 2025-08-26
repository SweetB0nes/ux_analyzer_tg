from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Привязка к целям/вопросам брифа.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки для строк с JSON, чтобы не экранировать "
    + """{"goal_links":["Прозрачность цены → рост CR онбординга"],"question_links":["Почему бросают? → не видят итоговую сумму"],"quotes":[{"text":"Где видно итого?"}]}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последней двойной кавычки
    + """{"goal_links":["string"],"question_links":["string"],"quotes":[{"text":"string"}]}\n"""
    + "{format_instructions}\n"
    + "ТЕКСТ:\n----\n{transcript_chunk}\n----\n"
    + GUARDRAILS
)

PROMPT = PromptTemplate.from_template(TEMPLATE)
