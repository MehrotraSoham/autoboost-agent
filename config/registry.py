from config.models import Post, LocationBaseline

# In-memory store — tools look up post/baseline data by ID.
# In production this would be a database query.
_posts: dict[str, Post] = {}
_baselines: dict[str, LocationBaseline] = {}


def register(post: Post, baseline: LocationBaseline) -> None:
    _posts[post.post_id] = post
    _baselines[post.location_id] = baseline


def get_post(post_id: str) -> Post:
    if post_id not in _posts:
        raise KeyError(f"Post '{post_id}' not found in registry")
    return _posts[post_id]


def get_baseline(location_id: str) -> LocationBaseline:
    if location_id not in _baselines:
        raise KeyError(f"Baseline for location '{location_id}' not found in registry")
    return _baselines[location_id]


def load_sample_data() -> None:
    """Populate the registry from data/sample_posts.json for local dev and demos."""
    import json
    from pathlib import Path
    from datetime import datetime, timezone

    path = Path(__file__).parent.parent / "data" / "sample_posts.json"
    data = json.loads(path.read_text())

    baselines = {
        loc_id: LocationBaseline(**b)
        for loc_id, b in data["baselines"].items()
    }

    for raw in data["posts"]:
        raw = {k: v for k, v in raw.items() if not k.startswith("_")}
        if isinstance(raw["published_at"], str):
            raw["published_at"] = datetime.fromisoformat(
                raw["published_at"].replace("Z", "+00:00")
            )
        post = Post(**raw)
        baseline = baselines[post.location_id]
        register(post, baseline)
