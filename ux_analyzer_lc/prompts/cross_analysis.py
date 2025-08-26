from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Кросс-анализ агрегатов.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"patterns":["Оплата — главный стоп-фактор"],"frequencies":{"непонятна_цена":5},"risks":["Доп. экраны приводят к отказам"],"vertical_slices":{"новички":["путаются"],"возвращающиеся":["торопятся"]}}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последней двойной кавычки в схеме
    + """{"patterns":["string"],"frequencies":{"item":3},"risks":["string"],"vertical_slices":{"slice":["item1","item2"]}}\n"""
    + "{format_instructions}\n"
    + "ДАННЫЕ:\n----\n{aggregates}\n----\n"
    + GUARDRAILS
)

PROMPT = PromptTemplate.from_template(TEMPLATE)
