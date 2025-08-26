from .base import build_from_prompt
from ux_analyzer_lc.prompts.patterns import PROMPT
from ux_analyzer_lc.schemas.patterns import Patterns

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=Patterns,
        input_keys=["brief_context", "aggregates", "min_quote_length"],
    )