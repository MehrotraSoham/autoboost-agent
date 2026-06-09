from config.models import Post, LocationBaseline, ScoreResult

WEIGHTS = {
    "comments": 0.30,
    "shares": 0.25,
    "saves": 0.20,
    "reach_velocity": 0.15,
    "likes": 0.10,
}

# Maps post age bucket to the corresponding baseline field on LocationBaseline
_REACH_BASELINE_FIELD = {
    "0-2h": "avg_reach_0_2h",
    "2-6h": "avg_reach_2_6h",
    "6-12h": "avg_reach_6_12h",
    "12-24h": "avg_reach_12_24h",
}


def _age_bucket(post_age_hours: float) -> str:
    if post_age_hours <= 2:
        return "0-2h"
    elif post_age_hours <= 6:
        return "2-6h"
    elif post_age_hours <= 12:
        return "6-12h"
    return "12-24h"


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator > 0 else 0.0


def score(post: Post, baseline: LocationBaseline, threshold: float = 1.5) -> ScoreResult:
    """
    Compute the composite engagement score for a post.

    Each signal is normalized against the location's 90-day average so that
    scores are comparable across locations with very different follower sizes.
    A score of 1.0 = exactly at baseline; 1.5 = 50% above baseline.
    """
    bucket = _age_bucket(post.post_age_hours)
    baseline_reach = getattr(baseline, _REACH_BASELINE_FIELD[bucket])

    norm_comments = _safe_div(post.comments_count, baseline.avg_comments)
    norm_shares = _safe_div(post.shares_count, baseline.avg_shares)
    norm_saves = _safe_div(post.saves_count, baseline.avg_saves)
    norm_reach = _safe_div(post.reach, baseline_reach)
    norm_likes = _safe_div(post.likes_count, baseline.avg_likes)

    composite = (
        norm_comments * WEIGHTS["comments"]
        + norm_shares * WEIGHTS["shares"]
        + norm_saves * WEIGHTS["saves"]
        + norm_reach * WEIGHTS["reach_velocity"]
        + norm_likes * WEIGHTS["likes"]
    )

    return ScoreResult(
        post_id=post.post_id,
        composite_score=round(composite, 3),
        triggered=composite > threshold,
        breakdown={
            "comments": round(norm_comments, 3),
            "shares": round(norm_shares, 3),
            "saves": round(norm_saves, 3),
            "reach_velocity": round(norm_reach, 3),
            "likes": round(norm_likes, 3),
        },
        threshold=threshold,
    )
