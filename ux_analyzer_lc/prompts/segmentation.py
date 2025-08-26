from __future__ import annotations
from langchain.prompts import PromptTemplate
from .common import SYSTEM_BASE, GUARDRAILS

TEMPLATE = (
    SYSTEM_BASE
    + "Отвечай ТОЛЬКО валидным JSON без Markdown и пояснений.\n\n"
    + "{brief_context}\n"
    + "ЗАДАЧА: 3–5 сегментов. Для каждого: имя, критерий сегментации, примерная доля/размер (size_hint), примеры id интервью, 1–3 ключевые боли/нужды, 1 цитата.\n"
    + "Мини-пример JSON:\n"
    # Используем тройные кавычки и убираем экранирование внутренних двойных кавычек
    + """{"segments":[{"name":"Новички","criteria":"Первый платёж","size_hint":"~35%","interview_ids":["int1","int3"],"key_pains":["Не видит итоговую сумму"],"key_needs":["Прозрачность цены"],"quotes":[{"text":"Хочу видеть итого заранее"}]}]}\n"""
    + """Схема ответа (строго):\n"""
    # Убираем экранирование последних двойных кавычек в схеме
    + """{"segments":[{"name":"..","criteria":"..","size_hint":"..","interview_ids":["id1"],"key_pains":[".."],"key_needs":[".."],"quotes":[{"text":".."}]}]}\n"""
    + "{format_instructions}\n"
    + "ДАННЫЕ:\n----\n{aggregates}\n----\n"
    + GUARDRAILS
)
PROMPT = PromptTemplate.from_template(TEMPLATE)
