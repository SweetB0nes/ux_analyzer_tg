from .base import build_from_prompt
from ux_analyzer_lc.prompts.personas import PROMPT
from ux_analyzer_lc.schemas.personas import Personas

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=Personas,
        input_keys=["brief_context", "aggregates", "min_quote_length"],
    )