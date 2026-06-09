from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Post(BaseModel):
    post_id: str
    location_id: str
    brand_id: str
    platform: str = "facebook"
    content: str = ""
    published_at: datetime
    post_age_hours: float = 0.0

    # Engagement signals
    comments_count: int = 0
    shares_count: int = 0
    saves_count: int = 0
    likes_count: int = 0
    reach: int = 0

    # Reaction breakdown — used by negativity filter stage 1
    angry_reactions: int = 0
    sad_reactions: int = 0
    total_reactions: int = 0

    # Recent comment text — used by negativity filter stage 2
    recent_comments: list[str] = Field(default_factory=list)


class LocationBaseline(BaseModel):
    location_id: str
    avg_comments: float
    avg_shares: float
    avg_saves: float
    avg_likes: float
    # Reach averages bucketed by post age (matches scoring window spec)
    avg_reach_0_2h: float
    avg_reach_2_6h: float
    avg_reach_6_12h: float
    avg_reach_12_24h: float


class ScoreResult(BaseModel):
    post_id: str
    composite_score: float
    triggered: bool
    breakdown: dict[str, float]
    threshold: float


class FilterResult(BaseModel):
    post_id: str
    passed: bool
    suppressed_reason: Optional[str] = None
    negative_reaction_ratio: float = 0.0
    negative_comment_ratio: float = 0.0


class BoostResult(BaseModel):
    post_id: str
    submitted: bool
    campaign_id: Optional[str] = None
    audience_id: Optional[str] = None
    budget: float = 0.0
    message: str = ""
