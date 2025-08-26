from .base import build_from_prompt
from ux_analyzer_lc.prompts.brief_questions import PROMPT
from ux_analyzer_lc.schemas.brief_questions import BriefQuestions

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=BriefQuestions,
        input_keys=["brief_context", "aggregates", "min_quote_length"],
    )