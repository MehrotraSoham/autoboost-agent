"""
Quick pipeline test — runs sample posts through the full agent.

Pass a post_id as an argument to test a single post:
  uv run python test_pipeline.py post-viral-001

Or run all posts (uses multiple API calls — space them out):
  uv run python test_pipeline.py
"""
import asyncio
import sys
from config.registry import load_sample_data
from agent.agent import process_post

load_sample_data()

ALL_CASES = [
    ("post-normal-002",   "Below threshold — expect no action"),
    ("post-negative-003", "Negative reactions — expect suppression"),
    ("post-viral-001",    "Viral post, APPROVAL mode"),
    ("post-auto-004",     "Viral post, AUTONOMOUS mode"),
    ("post-notify-005",   "Viral post, NOTIFY_ONLY mode"),
]


async def run_test(post_id: str, description: str) -> None:
    print(f"\n{'=' * 55}")
    print(f"  {description}")
    print(f"  post_id: {post_id}")
    print("=" * 55)
    result = await process_post(post_id)
    print(f"\n  RESULT: {result}")


async def main() -> None:
    # Single post mode: uv run python test_pipeline.py post-viral-001
    if len(sys.argv) > 1:
        post_id = sys.argv[1]
        match = next((c for c in ALL_CASES if c[0] == post_id), None)
        description = match[1] if match else "Custom post"
        await run_test(post_id, description)
        return

    # Full suite — small delay between posts to respect API rate limits
    for post_id, description in ALL_CASES:
        await run_test(post_id, description)
        await asyncio.sleep(2)


asyncio.run(main())
