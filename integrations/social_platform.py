"""
Source platform integration — mock client and engagement event simulator.

In production: replace SocialPlatformClient.fetch_active_posts() with real
API calls to the source platform's REST API. The event format
(EngagementEvent) stays the same, so the rest of the pipeline needs no
changes.
"""
import asyncio
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Awaitable

from config.models import Post, LocationBaseline
from config.registry import load_sample_data, get_post, _posts, _baselines


class EngagementEvent:
    def __init__(self, post_id: str, location_id: str, brand_id: str):
        self.post_id = post_id
        self.location_id = location_id
        self.brand_id = brand_id
        self.timestamp = datetime.now(timezone.utc)


EventHandler = Callable[[EngagementEvent], Awaitable[None]]


class SocialPlatformClient:
    """
    Mock source platform client. Exposes the same interface a real client
    would, so swapping in the real platform API is a one-file change.
    """

    def __init__(self, mock: bool = True):
        self.mock = mock
        if mock:
            load_sample_data()

    def fetch_active_posts(self) -> list[tuple[Post, LocationBaseline]]:
        """Return all posts currently in the monitoring window (0–72 hrs)."""
        results = []
        for post_id, post in _posts.items():
            if post.post_age_hours <= 72:
                baseline = _baselines.get(post.location_id)
                if baseline:
                    results.append((post, baseline))
        return results

    async def simulate_engagement_spike(
        self,
        post_id: str,
        handler: EventHandler,
        delay_secs: float = 0.5,
    ) -> None:
        """Fire a single engagement event — used by the simulator and tests."""
        await asyncio.sleep(delay_secs)
        post = get_post(post_id)
        event = EngagementEvent(
            post_id=post.post_id,
            location_id=post.location_id,
            brand_id=post.brand_id,
        )
        print(
            f"[Source platform mock] Engagement spike fired → post_id={post_id} "
            f"brand_id={post.brand_id}"
        )
        await handler(event)

    async def run_simulator(self, handler: EventHandler) -> None:
        """
        Fire all sample posts as engagement events with a short stagger.
        Simulates a real-time stream of source platform webhook events.
        """
        print("[Source platform mock] Starting engagement simulator...")
        post_ids = list(_posts.keys())
        tasks = [
            self.simulate_engagement_spike(pid, handler, delay_secs=i * 1.5)
            for i, pid in enumerate(post_ids)
        ]
        await asyncio.gather(*tasks)
        print("[Source platform mock] Simulator complete.")
