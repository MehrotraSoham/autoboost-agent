from langchain_core.tools import tool

from agent import engine
from config.registry import get_post, get_baseline
from config.brand_config import get_brand_config


@tool
def score_post(post_id: str) -> dict:
    """
    Score a franchise post's composite engagement against its location 90-day baseline.
    Returns the composite score, whether it crossed the brand's threshold (triggered),
    and a breakdown by signal (comments, shares, saves, reach_velocity, likes).
    """
    post = get_post(post_id)
    baseline = get_baseline(post.location_id)
    config = get_brand_config(post.brand_id)

    result = engine.score(post, baseline, threshold=config.score_threshold)
    return result.model_dump()
