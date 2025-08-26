from .base import build_from_prompt
from ux_analyzer_lc.prompts.quotes_and_contradictions import PROMPT
from ux_analyzer_lc.schemas.quotes_and_contradictions import QuotesAndContradictions

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=QuotesAndContradictions,
        input_keys=["brief_context", "transcript_chunk", "min_quote_length"],
    )