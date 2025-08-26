from .base import build_from_prompt
from ux_analyzer_lc.prompts.emotions_and_insights import PROMPT
from ux_analyzer_lc.schemas.emotions_and_insights import EmotionsAndInsights

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=EmotionsAndInsights,
        input_keys=["brief_context", "transcript_chunk", "min_quote_length"],
    )