"""
AutoBoost LangChain Agent

Uses LangGraph's prebuilt ReAct agent with Claude as the backbone.
The agent receives a post event, then decides which tools to call and
in what order — guided by a system prompt that encodes the AutoBoost
decision process.

LangSmith tracing is enabled automatically when LANGCHAIN_TRACING_V2=true
and LANGCHAIN_API_KEY are set in the environment. View traces at
smith.langchain.com to see every tool call, LLM reasoning step, and token usage.
"""
import os
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from agent.tools import ALL_TOOLS
from config.brand_config import get_brand_config, settings
from config.llm import get_llm
from config.registry import get_post

# LangSmith reads these directly from the environment.
# We sync them from pydantic-settings so .env is the single source of truth.
os.environ.setdefault("LANGCHAIN_TRACING_V2", str(settings.langchain_tracing_v2).lower())
if settings.langchain_api_key:
    os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
os.environ.setdefault("LANGCHAIN_PROJECT", settings.langchain_project)

SYSTEM_PROMPT = """You are AutoBoost, an AI agent that decides whether \
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
    """Create the LangChain ReAct agent with the configured LLM provider."""
    llm = get_llm(max_tokens=1024)
    return create_react_agent(llm, tools=ALL_TOOLS, prompt=SYSTEM_PROMPT)


async def process_post(post_id: str) -> str:
    """
    Entry point for processing a single post event.
    Called by the webhook handler and the polling scheduler.
    """
    post = get_post(post_id)
    config = get_brand_config(post.brand_id)

    agent = build_agent()
    message = (
        f"Process post_id='{post_id}' for brand_id='{post.brand_id}'. "
        f"The boost_mode for this brand is {config.boost_mode.value}."
    )

    print(f"\n[Agent] Processing {post_id} (mode={config.boost_mode.value})...")
    result = await agent.ainvoke({"messages": [HumanMessage(content=message)]})

    # Find the last non-empty AI message — tool errors leave ToolMessages at the end
    from langchain_core.messages import AIMessage
    final_message = next(
        (m.content for m in reversed(result["messages"]) if isinstance(m, AIMessage) and m.content),
        "Agent completed with no final message."
    )
    print(f"[Agent] Done — {post_id}: {final_message}\n")
    return final_message
