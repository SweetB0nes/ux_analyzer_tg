# ux_analyzer_lc/chains/profile_and_themes.py
from .base import build_from_prompt
from ux_analyzer_lc.prompts.profile_and_themes import PROMPT
from ux_analyzer_lc.schemas.profile_and_themes import ProfileAndThemes

def build():
    # используем brief_context + transcript_chunk
    return build_from_prompt(
        template=PROMPT,
        schema=ProfileAndThemes,
        input_keys=["brief_context", "transcript_chunk", "min_quote_length"],
    )