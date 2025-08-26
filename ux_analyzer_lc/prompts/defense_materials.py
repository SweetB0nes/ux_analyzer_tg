from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Материалы для защиты: key findings, критические риски, assumptions, next steps, критерии решения, метрики трекинга.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"key_findings":["Нет видимости итоговой суммы"],"critical_risks":["Отказы на шаге оплаты"],"assumptions":["Прозрачность снизит отказы"],"next_steps":["Прототип экрана с итоговой суммой"],"decision_criteria":["CR +5 п.п."],"tracking_metrics":["CR","NPS"]}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последних двойных кавычек в схеме
    + """{"key_findings":[".."],"critical_risks":[".."],"assumptions":[".."],"next_steps":[".."],"decision_criteria":[".."],"tracking_metrics":[".."]}\n"""
    + "{format_instructions}\n"
    + "ДАННЫЕ:\n----\n{aggregates}\n----\n"
    + GUARDRAILS
)

PROMPT = PromptTemplate.from_template(TEMPLATE)
