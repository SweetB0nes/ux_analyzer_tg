# ux_analyzer_lc/chains/base.py
from __future__ import annotations
import os
from typing import Iterable, Sequence, Union

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser

from ux_analyzer_lc.llm_providers import LLMFactory


def _ensure_set(x: Iterable[str] | None) -> set[str]:
    return set(x) if x else set()


def _escape_but_keep_placeholders(text: str, required: set[str]) -> str:
    """
    Экранируем все { } в тексте, затем откатываем реальные плейсхолдеры из required.
    Это защищает JSON-примеры внутри промптов.
    """
    escaped = text.replace("{", "{{").replace("}", "}}")
    for name in required:
        # точный плейсхолдер
        escaped = escaped.replace("{{" + name + "}}", "{" + name + "}")
        # на случай формата {{ name }}
        escaped = escaped.replace("{{ " + name + " }}", "{" + name + "}")
    return escaped


def _collect_required_variables(raw: str, base_keys: Sequence[str], include_format_instructions: bool) -> set[str]:
    required = _ensure_set(base_keys)
    if include_format_instructions or "{format_instructions" in raw:
        required.add("format_instructions")
    # min_quote_length иногда нужен цепочкам — делаем его optional через partial,
    # но добавим в required, если он реально встречается в шаблоне
    if "{min_quote_length" in raw:
        required.add("min_quote_length")
    return required


def _append_format_instructions_if_missing(raw: str) -> str:
    """
    Если в шаблоне нет {format_instructions}, добавляем в конец с жёсткой установкой
    «верни только валидный JSON».
    """
    if "{format_instructions" in raw:
        return raw
    suffix = (
        "\n\n"
        "FORMAT:\n"
        "{format_instructions}\n\n"
        "Return ONLY valid JSON that matches the schema above. No prose, no markdown."
    )
    return raw + suffix


def build_from_prompt(
    template: Union[str, PromptTemplate],
    schema,                       # pydantic model
    input_keys: Sequence[str] = (),   # какие переменные будут приходить при вызове .invoke(...)
    default_min_quote: int | None = None,  # дефолт для min_quote_length (если нужен)
) -> Runnable:
    """
    Универсальный билдер:
    - принимает строку или PromptTemplate;
    - экранирует фигурные скобки, сохраняя реальные плейсхолдеры;
    - гарантированно добавляет {format_instructions} в текст промпта;
    - задаёт partial для min_quote_length, если он встречается и не приходит на вызове.
    """
    # сырой текст шаблона
    if isinstance(template, PromptTemplate):
        raw = template.template
    else:
        raw = str(template)

    # убедимся, что в текст действительно попали format_instructions
    raw = _append_format_instructions_if_missing(raw)

    parser = PydanticOutputParser(pydantic_object=schema)

    # список требуемых плейсхолдеров
    required = _collect_required_variables(
        raw=raw,
        base_keys=input_keys,
        include_format_instructions=True,
    )

    # экранируем лишние скобки, но сохраняем нужные плейсхолдеры
    safe_template = _escape_but_keep_placeholders(raw, required)

    # partial-переменные
    partials = {
        "format_instructions": parser.get_format_instructions()
    }

    # дефолтная длина цитаты — из аргумента, а если его нет, из env-переменной, иначе 40
    if "min_quote_length" in required:
        default_val = (
            default_min_quote
            if default_min_quote is not None
            else int(os.getenv("UX_MIN_QUOTE_LENGTH", "40"))
        )
        partials["min_quote_length"] = str(default_val)

    prompt = PromptTemplate(
        template=safe_template,
        input_variables=sorted(_ensure_set(input_keys) | ({"format_instructions"} if "{format_instructions" in safe_template else set())),
        partial_variables=partials,
    )

    llm = LLMFactory.make_chat_model()

    # prompt -> llm -> строка -> pydantic
    chain: Runnable = prompt | llm | StrOutputParser() | parser
    return chain
