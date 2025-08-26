from .base import build_from_prompt
from ux_analyzer_lc.prompts.cross_analysis import PROMPT
from ux_analyzer_lc.schemas.cross_analysis import CrossAnalysis

def build():
    # тут анализ по агрегатам, а не по одному транскрипту
    return build_from_prompt(
        template=PROMPT,
        schema=CrossAnalysis,
        input_keys=["brief_context", "aggregates", "min_quote_length"],
    )