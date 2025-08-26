from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Достижение целей (achieved/partial/not), обоснования, уверенность, пробелы, действия.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"goals":[{"goal":"CR онбординга +10%","status":"partial","rationale":"Есть возможности по видимости цены","confidence":0.6,"gaps":["Требуется A/B"],"required_actions":["Прототип","Тест"]}]}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последних двойных кавычек в схеме
    + """{"goals":[{"goal":"..","status":"achieved|partial|not","rationale":"..","confidence":0.0,"gaps":[".."],"required_actions":[".."]}]}\n"""
    + "{format_instructions}\n"
    + "ДАННЫЕ:\n----\n{aggregates}\n----\n"
    + GUARDRAILS
)

PROMPT = PromptTemplate.from_template(TEMPLATE)
