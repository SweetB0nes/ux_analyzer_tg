from .base import build_from_prompt
from ux_analyzer_lc.prompts.segmentation import PROMPT
from ux_analyzer_lc.schemas.segmentation import Segmentation

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=Segmentation,
        input_keys=["brief_context", "aggregates", "min_quote_length"],
    )