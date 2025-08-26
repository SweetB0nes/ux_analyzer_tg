from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: Ответы на вопросы брифа, источники-интервью и цитаты.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"answers":[{"question":"Почему бросают оплату?","answer":"Нет видимности итоговой суммы до подтверждения","evidence_quotes":[{"text":"Я не понял сколько спишут"}],"confidence":0.72,"interviews":["int1","int3"]}]}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последней двойной кавычки в схеме
    + """{"answers":[{"question":"..","answer":"..","evidence_quotes":[{"text":".."}],"confidence":0.0,"interviews":["id1"]}]}\n"""
    + "{format_instructions}\n"
    + "ДАННЫЕ:\n----\n{aggregates}\n----\n"
    + GUARDRAILS
)

PROMPT = PromptTemplate.from_template(TEMPLATE)
