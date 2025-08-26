from .base import build_from_prompt
from ux_analyzer_lc.prompts.pains_and_needs import PROMPT
from ux_analyzer_lc.schemas.pains_and_needs import PainsAndNeeds

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=PainsAndNeeds,
        input_keys=["brief_context", "transcript_chunk", "min_quote_length"],
    )