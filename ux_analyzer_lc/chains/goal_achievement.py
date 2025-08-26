from .base import build_from_prompt
from ux_analyzer_lc.prompts.goal_achievement import PROMPT
from ux_analyzer_lc.schemas.goal_achievement import GoalAchievement

def build():
    return build_from_prompt(
        template=PROMPT,
        schema=GoalAchievement,
        input_keys=["brief_context", "aggregates", "min_quote_length"],
    )