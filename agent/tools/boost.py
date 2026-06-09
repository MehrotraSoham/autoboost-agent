from langchain_core.tools import tool

from integrations import meta
from config.registry import get_post
from config.brand_config import get_brand_config


@tool
def submit_meta_boost(post_id: str) -> dict:
    """
    Build a dynamic lookalike audience from the post's organic engagers
    and submit a paid boost campaign to Meta Ads.

    Returns the campaign_id, audience_id, budget, and submission status.
    Currently runs against the Meta Ads stub — swap for Meta Ads MCP
    when real credentials are available.
    """
    post = get_post(post_id)
    config = get_brand_config(post.brand_id)

    audience_id = meta.build_lookalike_audience(post)
    result = meta.submit_boost(
        post=post,
        budget=config.default_boost_budget,
        audience_id=audience_id,
    )
    return result.model_dump()
