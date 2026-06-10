from langchain_core.tools import tool

from agent import filter as negativity_filter
from config.registry import get_post


@tool
async def run_negativity_filter(post_id: str) -> dict:
    """
    Run the two-stage negativity gate on a post before any spend fires.

    Stage 1: reaction ratio — suppresses if angry/sad reactions exceed 20% of total.
    Stage 2: comment sentiment via LLM — suppresses if negative comments exceed 30%.

    Returns passed (bool), suppressed_reason (if failed), and the ratio scores.
    """
    post = get_post(post_id)
    result = await negativity_filter.run(post)
    return result.model_dump()
