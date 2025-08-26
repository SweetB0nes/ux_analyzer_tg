from .base import build_from_prompt
from ux_analyzer_lc.prompts.brief_linkage import PROMPT
from ux_analyzer_lc.schemas.brief_linkage import BriefLinkage

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=BriefLinkage,
        input_keys=["brief_context", "transcript_chunk", "min_quote_length"],
    )