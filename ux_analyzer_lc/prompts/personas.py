from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Персоны (2–4). Для каждой: имя/ярлык, связанный сегмент, цели, блокеры, каналы, ключевые сценарии, 1–2 цитаты.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"personas":[{"name":"Осторожный новичок","segment":"Новички","goals":["Быстро понять стоимость"],"blockers":["Боится скрытых комиссий"],"channels":["Моб. приложение"],"scenarios":["Первый платеж"],"quotes":[{"text":"Хочу видеть, сколько спишут заранее"}]}]}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последних двойных кавычек в схеме
    + """{"personas":[{"name":"..","segment":"..","goals":[".."],"blockers":[".."],"channels":[".."],"scenarios":[".."],"quotes":[{"text":".."}]}]}\n"""
    + "{format_instructions}\n"
    + "ДАННЫЕ:\n----\n{aggregates}\n----\n"
    + GUARDRAILS
)
PROMPT = PromptTemplate.from_template(TEMPLATE)
