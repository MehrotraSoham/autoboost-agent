"""
AutoBoost LangChain Agent

Uses LangGraph's prebuilt ReAct agent with Claude as the backbone.
The agent receives a post event, then decides which tools to call and
in what order — guided by a system prompt that encodes the AutoBoost
decision process.
"""
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from agent.tools import ALL_TOOLS
from config.brand_config import get_brand_config, BoostMode, settings
from config.registry import get_post

SYSTEM_PROMPT = """You are AutoBoost, an AI agent for Ignite Visibility that decides whether \
to boost franchise social media posts with paid advertising.

When given a post_id and brand_id, follow this exact decision process:

1. Call score_post(post_id) to get the composite engagement score.
   - If triggered is false: report the score and stop. No further action.
   - If triggered is true: continue to step 2.

2. Call run_negativity_filter(post_id) to check for negative sentiment.
   - If passed is false: report the suppression reason and stop. No boost.
   - If passed is true: continue to step 3.

3. Route based on the boost_mode provided in the message:
   - AUTONOMOUS:   Call submit_meta_boost(post_id) immediately.
   - APPROVAL:     Call send_slack_notification(post_id, mode="APPROVAL").
                   If approved=true, call submit_meta_boost(post_id).
                   If approved=false, report suppression and stop.
   - NOTIFY_ONLY:  Call send_slack_notification(post_id, mode="NOTIFY_ONLY"). No boost.

4. Report the final outcome clearly: what happened, the score, and any campaign details.

Always complete the full process. Be concise and factual in your final report."""


def build_agent():
    """Create the LangChain ReAct agent with all AutoBoost tools."""
    llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        api_key=settings.anthropic_api_key or "mock-key",
        max_tokens=1024,
    )
    return create_react_agent(llm, tools=ALL_TOOLS, prompt=SYSTEM_PROMPT)


async def process_post(post_id: str) -> str:
    """
    Entry point for processing a single post event.
    Called by the webhook handler and the polling scheduler.
    """
    post = get_post(post_id)
    config = get_brand_config(post.brand_id)

    if not settings.anthropic_api_key:
        return await _run_without_llm(post_id, config.boost_mode)

    agent = build_agent()
    message = (
        f"Process post_id='{post_id}' for brand_id='{post.brand_id}'. "
        f"The boost_mode for this brand is {config.boost_mode.value}."
    )

    result = await agent.ainvoke({"messages": [HumanMessage(content=message)]})
    final_message = result["messages"][-1].content
    print(f"\n[Agent] Final response for {post_id}:\n{final_message}\n")
    return final_message


async def _run_without_llm(post_id: str, boost_mode: BoostMode) -> str:
    """
    Fallback pipeline when no Anthropic API key is set.
    Runs the same logic deterministically so the demo works without credentials.
    """
    from agent import engine, filter as neg_filter
    from integrations import slack, meta
    from config.registry import get_post, get_baseline
    from config.brand_config import get_brand_config

    post = get_post(post_id)
    baseline = get_baseline(post.location_id)
    config = get_brand_config(post.brand_id)

    # Step 1: Score
    score_result = engine.score(post, baseline, threshold=config.score_threshold)
    print(f"[Pipeline] {post_id} → score={score_result.composite_score} triggered={score_result.triggered}")

    if not score_result.triggered:
        return f"Post {post_id} scored {score_result.composite_score} — below threshold {score_result.threshold}. No action."

    # Step 2: Negativity filter
    filter_result = await neg_filter.run(post)
    print(f"[Pipeline] {post_id} → filter passed={filter_result.passed}")

    if not filter_result.passed:
        return f"Post {post_id} suppressed: {filter_result.suppressed_reason}"

    # Step 3: Route by boost mode
    if boost_mode == BoostMode.NOTIFY_ONLY:
        slack.send_notification(post, score_result, config.slack_channel_id)
        return f"Post {post_id} — NOTIFY_ONLY: Slack alert sent. No spend triggered."

    if boost_mode == BoostMode.APPROVAL:
        approved = await slack.send_approval_request(
            post, score_result, config.default_boost_budget,
            config.slack_channel_id, config.approval_timeout_mins,
        )
        if not approved:
            return f"Post {post_id} — suppressed by account manager (or timed out)."

    audience_id = meta.build_lookalike_audience(post)
    boost = meta.submit_boost(post, config.default_boost_budget, audience_id)
    return (
        f"Post {post_id} — boost submitted. "
        f"campaign_id={boost.campaign_id} budget=${boost.budget}"
    )
