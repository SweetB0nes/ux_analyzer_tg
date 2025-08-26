from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Рекомендации — категоризируй (quick_win | mid | strategic), укажи обоснование, усилие, влияние, риски, зависимости, метрики успеха.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"recommendations":[{"title":"Показывать итоговую стоимость на первом экране","category":"quick_win","rationale":"Снижает неопределенность на старте","effort":"низкий","impact":"высокий","risks":["Перегрузка интерфейса"],"dependencies":["Актуальные тарифы"],"success_metrics":["CR онбординга"]}]}"""
    + """\nСхема ответа (строго):\n"""
    # Убираем экранирование последних двойных кавычек в схеме
    + """{"recommendations":[{"title":"..","category":"quick_win|mid|strategic","rationale":"..","effort":"..","impact":"..","risks":[".."],"dependencies":[".."],"success_metrics":[".."]}]}\n"""
    + "{format_instructions}\n"
    + "ДАННЫЕ:\n----\n{aggregates}\n----\n"
    + GUARDRAILS
)
PROMPT = PromptTemplate.from_template(TEMPLATE)
