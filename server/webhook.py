"""
FastAPI webhook server.

Two endpoints:
  POST /webhook/engagement  — receives Rallio engagement events (real or mock)
  POST /webhook/slack       — receives Slack interactive component callbacks (Approve/Suppress)
"""
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

from agent.agent import process_post
from integrations.slack import resolve_approval
from config.registry import load_sample_data, get_post


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load sample data so posts are available in the registry on startup.
    # To run the full pipeline against the sample posts, use
    # `uv run python test_pipeline.py` (processes posts sequentially —
    # firing them all at once exceeds Gemini's free-tier rate limit).
    load_sample_data()
    yield


app = FastAPI(title="AutoBoost Agent", version="0.1.0", lifespan=lifespan)


class EngagementPayload(BaseModel):
    post_id: str
    location_id: str
    brand_id: str


@app.post("/webhook/engagement")
async def handle_engagement_event(payload: EngagementPayload):
    """
    Called by Rallio when a post's engagement changes.
    Kicks off the AutoBoost pipeline asynchronously so the webhook
    returns immediately (Rallio expects a fast 200 response).
    """
    try:
        get_post(payload.post_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Post '{payload.post_id}' not in registry. "
                   "Load it first via the Rallio client or sample data.",
        )

    asyncio.create_task(process_post(payload.post_id))
    return {"status": "accepted", "post_id": payload.post_id}


@app.post("/webhook/slack")
async def handle_slack_interaction(request: Request):
    """
    Called by Slack when an account manager clicks Approve or Suppress
    on an approval notification.
    """
    body = await request.body()

    # Slack sends interactive payloads as URL-encoded form data
    try:
        form = await request.form()
        payload = json.loads(form.get("payload", "{}"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Slack payload")

    actions = payload.get("actions", [])
    if not actions:
        return {"ok": True}

    action = actions[0]
    action_id = action.get("action_id", "")
    post_id = action.get("value", "")

    approved = action_id == "approve_boost"
    resolved = resolve_approval(post_id, approved)

    if not resolved:
        return {"ok": True, "note": "No pending approval found for this post"}

    action_label = "approved" if approved else "suppressed"
    print(f"[Slack webhook] Account manager {action_label} boost for post {post_id}")
    return {"ok": True, "action": action_label, "post_id": post_id}


@app.get("/health")
async def health():
    return {"status": "ok"}
