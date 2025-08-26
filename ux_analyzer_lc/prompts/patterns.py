from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Поведенческие паттерны — повторяющиеся действия/реакции пользователей, выявленные в интервью.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"behavioral_patterns":["Пользователь ищет итоговую сумму перед вводом карты","Скроллит до блоков с примерами перед началом формы"]}\n"""
    + """Схема ответа (строго): {"behavioral_patterns":["string"]}\n"""
    + "{format_instructions}\n"
    + "ДАННЫЕ:\n----\n{aggregates}\n----\n"
    + GUARDRAILS
)
PROMPT = PromptTemplate.from_template(TEMPLATE)
