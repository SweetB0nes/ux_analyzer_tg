from .base import build_from_prompt
from ux_analyzer_lc.prompts.business_aspects import PROMPT
from ux_analyzer_lc.schemas.business_aspects import BusinessAspects

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=BusinessAspects,
        input_keys=["brief_context", "transcript_chunk", "min_quote_length"],
    )