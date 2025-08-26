from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Итоговые выводы (executive summary, ключевые инсайты, риски, assumptions, рекомендации, персоны).\n"
    + "Формат: JSON по схеме Findings (твоя pydantic-схема Findings).\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"executive_summary":"Главный стоп-фактор — непрозрачность цены перед оплатой.","key_insights":["Нет видимости итоговой суммы","Доп. шаг подтверждения"],"risks":["Потеря конверсии на оплате"],"assumptions":["Прозрачность цены снизит отказы"],"recommendations":["Показать итоговую сумму заранее","Сократить шаги оплаты"],"personas":[{"name":"Новичок","traits":["осторожен","боится скрытых платежей"]}]}\n"""
    + "{format_instructions}\n"
    + "ДАННЫЕ:\n----\n{aggregates}\n----\n"
    + GUARDRAILS
)

PROMPT = PromptTemplate.from_template(TEMPLATE)
