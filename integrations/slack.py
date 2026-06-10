"""
Slack integration — sends approval notifications and handles responses.

Uses the Slack SDK when SLACK_BOT_TOKEN is set.
Falls back to console output in mock mode so the agent runs without credentials.
"""
import asyncio
from typing import Optional

from config.brand_config import settings
from config.models import Post, ScoreResult

# Holds pending approval futures keyed by post_id.
# The /webhook/slack endpoint resolves these when the account manager acts.
_pending_approvals: dict[str, asyncio.Future] = {}


async def send_approval_request(
    post: Post,
    score: ScoreResult,
    budget: float,
    channel_id: str,
    timeout_mins: int = 60,
) -> bool:
    """
    Send an approval notification to Slack and wait for a response.
    Returns True if approved, False if suppressed or timed out.
    """
    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()
    _pending_approvals[post.post_id] = future

    _send_slack_message(
        channel_id=channel_id,
        post=post,
        score=score,
        budget=budget,
        mode="APPROVAL",
    )

    try:
        approved = await asyncio.wait_for(future, timeout=timeout_mins * 60)
        return approved
    except asyncio.TimeoutError:
        print(
            f"[Slack] Approval for post {post.post_id} timed out after "
            f"{timeout_mins} min — suppressing."
        )
        return False
    finally:
        _pending_approvals.pop(post.post_id, None)


def send_notification(
    post: Post,
    score: ScoreResult,
    channel_id: str,
) -> None:
    """Send a fire-and-forget notification (NOTIFY_ONLY mode)."""
    _send_slack_message(
        channel_id=channel_id,
        post=post,
        score=score,
        budget=0,
        mode="NOTIFY_ONLY",
    )


def resolve_approval(post_id: str, approved: bool) -> bool:
    """
    Called by the /webhook/slack endpoint when an account manager
    clicks Approve or Suppress in Slack.
    """
    future = _pending_approvals.get(post_id)
    if not future or future.done():
        return False
    future.set_result(approved)
    return True


def _send_slack_message(
    channel_id: str,
    post: Post,
    score: ScoreResult,
    budget: float,
    mode: str,
) -> None:
    if settings.slack_bot_token and channel_id:
        _send_real_slack_message(channel_id, post, score, budget, mode)
    else:
        _print_mock_slack_message(post, score, budget, mode)


def _print_mock_slack_message(
    post: Post,
    score: ScoreResult,
    budget: float,
    mode: str,
) -> None:
    action = "APPROVAL REQUESTED" if mode == "APPROVAL" else "PERFORMANCE ALERT"
    print(f"\n{'=' * 60}")
    print(f"[Slack mock] {action}")
    print(f"  Post ID   : {post.post_id}")
    print(f"  Brand     : {post.brand_id}")
    print(f"  Score     : {score.composite_score} (threshold: {score.threshold})")
    print(f"  Breakdown : {score.breakdown}")
    print(f"  Content   : {post.content[:80]}...")
    if mode == "APPROVAL":
        print(f"  Budget    : ${budget}")
        print(f"  Actions   : [Approve] [Suppress]")
    print("=" * 60 + "\n")


def _send_real_slack_message(
    channel_id: str,
    post: Post,
    score: ScoreResult,
    budget: float,
    mode: str,
) -> None:
    import ssl
    import certifi
    from slack_sdk import WebClient

    client = WebClient(
        token=settings.slack_bot_token,
        ssl=ssl.create_default_context(cafile=certifi.where()),
    )
    action = "Approval Requested" if mode == "APPROVAL" else "Performance Alert"

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"AutoBoost — {action}"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Post ID:*\n{post.post_id}"},
                {"type": "mrkdwn", "text": f"*Brand:*\n{post.brand_id}"},
                {
                    "type": "mrkdwn",
                    "text": f"*Score:*\n{score.composite_score} (threshold: {score.threshold})",
                },
                {"type": "mrkdwn", "text": f"*Budget:*\n${budget}"},
            ],
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Content:*\n{post.content[:200]}"},
        },
    ]

    if mode == "APPROVAL":
        blocks.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "action_id": "approve_boost",
                        "value": post.post_id,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Suppress"},
                        "style": "danger",
                        "action_id": "suppress_boost",
                        "value": post.post_id,
                    },
                ],
            }
        )

    client.chat_postMessage(channel=channel_id, blocks=blocks)
