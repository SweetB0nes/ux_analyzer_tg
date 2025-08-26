from .base import build_from_prompt
from ux_analyzer_lc.prompts.final_findings import PROMPT
from ux_analyzer_lc.schemas.final_findings import Findings

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=Findings,
        input_keys=["brief_context", "aggregates", "min_quote_length"],
    )