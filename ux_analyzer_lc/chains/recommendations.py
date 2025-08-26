from .base import build_from_prompt
from ux_analyzer_lc.prompts.recommendations import PROMPT
from ux_analyzer_lc.schemas.recommendations import Recommendations

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=Recommendations,
        input_keys=["brief_context", "aggregates", "min_quote_length"],
    )