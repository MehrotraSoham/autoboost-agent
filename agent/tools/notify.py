import asyncio
from langchain_core.tools import tool

from integrations import slack
from config.registry import get_post
from config.brand_config import get_brand_config
from agent import engine
from config.registry import get_baseline


@tool
def send_slack_notification(post_id: str, mode: str = "APPROVAL") -> dict:
    """
    Send a Slack notification to the account manager.

    mode=APPROVAL  — sends an interactive approval card and waits for a response.
                     Returns {"approved": true/false, "action": "approved"/"suppressed"/"timeout"}
    mode=NOTIFY_ONLY — sends a fire-and-forget performance alert. No spend is triggered.
                     Returns {"notified": true}
    """
    post = get_post(post_id)
    config = get_brand_config(post.brand_id)
    baseline = get_baseline(post.location_id)
    score_result = engine.score(post, baseline, threshold=config.score_threshold)

    if mode == "NOTIFY_ONLY":
        slack.send_notification(
            post=post,
            score=score_result,
            channel_id=config.slack_channel_id,
        )
        return {"notified": True, "post_id": post_id}

    # APPROVAL mode — wait for account manager response
    approved = asyncio.run(
        slack.send_approval_request(
            post=post,
            score=score_result,
            budget=config.default_boost_budget,
            channel_id=config.slack_channel_id,
            timeout_mins=config.approval_timeout_mins,
        )
    )
    return {
        "approved": approved,
        "action": "approved" if approved else "suppressed",
        "post_id": post_id,
    }
