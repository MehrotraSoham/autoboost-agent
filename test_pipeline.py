"""
Quick pipeline test — runs all 5 sample posts without needing a server or API keys.
"""
import asyncio
from config.registry import load_sample_data
from agent.agent import process_post

load_sample_data()

async def main():
    test_cases = [
        ("post-normal-002",   "Below threshold — expect no action"),
        ("post-negative-003", "Negative reactions — expect suppression"),
        ("post-viral-001",    "Viral post, APPROVAL mode"),
        ("post-auto-004",     "Viral post, AUTONOMOUS mode"),
        ("post-notify-005",   "Viral post, NOTIFY_ONLY mode"),
    ]

    for post_id, description in test_cases:
        print(f"\n{'=' * 55}")
        print(f"  {description}")
        print(f"  post_id: {post_id}")
        print("=" * 55)
        result = await process_post(post_id)
        print(f"\n  RESULT: {result}")

asyncio.run(main())
