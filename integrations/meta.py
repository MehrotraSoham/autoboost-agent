"""
Meta Ads integration — stub ready for Meta Ads MCP.

All methods log what they would do and return realistic-looking mock data.
Swap the internals of submit_boost() for real Meta Ads MCP calls when
your client has Meta Business account credentials.
"""
import uuid
from config.models import Post, BoostResult
from config.brand_config import settings


def build_lookalike_audience(post: Post) -> str:
    """
    In production: call Meta Insights API to pull demographic profile
    of the post's organic engagers, then create a Custom Audience +
    Lookalike Audience seeded from those engagers.

    Returns the audience_id to attach to the boost campaign.
    """
    audience_id = f"aud_{uuid.uuid4().hex[:12]}"
    print(
        f"[Meta stub] Built lookalike audience from organic engagers "
        f"of post {post.post_id} → audience_id={audience_id}"
    )
    return audience_id


def submit_boost(post: Post, budget: float, audience_id: str) -> BoostResult:
    """
    In production: use Meta Ads MCP to create a campaign, ad set (using
    audience_id), and ad creative from the post, then submit for review.

    Meta Ads MCP (announced April 2026) reduces review time to near-instant
    when pre-approved ad templates are used.
    """
    real_token = (
        settings.meta_access_token
        and settings.meta_access_token != "your_meta_access_token"
    )
    if real_token:
        return _submit_real_boost(post, budget, audience_id)

    return _submit_mock_boost(post, budget, audience_id)


def _submit_mock_boost(post: Post, budget: float, audience_id: str) -> BoostResult:
    campaign_id = f"camp_{uuid.uuid4().hex[:12]}"
    print(
        f"[Meta stub] Boost submitted:\n"
        f"  post_id     = {post.post_id}\n"
        f"  campaign_id = {campaign_id}\n"
        f"  audience_id = {audience_id}\n"
        f"  budget      = ${budget}\n"
        f"  platform    = {post.platform}"
    )
    return BoostResult(
        post_id=post.post_id,
        submitted=True,
        campaign_id=campaign_id,
        audience_id=audience_id,
        budget=budget,
        message=f"[Mock] Boost campaign {campaign_id} submitted successfully.",
    )


def _submit_real_boost(post: Post, budget: float, audience_id: str) -> BoostResult:
    # TODO: replace with Meta Ads MCP tool calls
    raise NotImplementedError(
        "Real Meta Ads integration not yet implemented. "
        "Swap this with Meta Ads MCP calls when credentials are available."
    )
