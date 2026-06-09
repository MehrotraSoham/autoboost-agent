from enum import Enum
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BoostMode(str, Enum):
    AUTONOMOUS = "AUTONOMOUS"
    APPROVAL = "APPROVAL"
    NOTIFY_ONLY = "NOTIFY_ONLY"


class BrandConfig(BaseModel):
    brand_id: str
    brand_name: str
    boost_mode: BoostMode = BoostMode.APPROVAL
    score_threshold: float = 1.5
    monthly_budget_cap: float = 500.0
    default_boost_budget: float = 50.0
    approval_timeout_mins: int = 60
    slack_channel_id: str = ""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    slack_bot_token: str = ""
    slack_channel_id: str = ""
    meta_access_token: str = ""
    meta_ad_account_id: str = ""

    boost_mode: BoostMode = BoostMode.APPROVAL
    score_threshold: float = 1.5
    monthly_budget_cap: float = 500.0
    default_boost_budget: float = 50.0
    approval_timeout_mins: int = 60


settings = Settings()

# Sample brand registry — in production this comes from a database
BRAND_REGISTRY: dict[str, BrandConfig] = {
    "demo-brand": BrandConfig(
        brand_id="demo-brand",
        brand_name="Demo Franchise Brand",
        boost_mode=BoostMode.APPROVAL,
        score_threshold=1.5,
        monthly_budget_cap=500.0,
        default_boost_budget=50.0,
        approval_timeout_mins=60,
        slack_channel_id=settings.slack_channel_id,
    ),
    "auto-brand": BrandConfig(
        brand_id="auto-brand",
        brand_name="Auto-Approve Brand",
        boost_mode=BoostMode.AUTONOMOUS,
        score_threshold=2.0,
        monthly_budget_cap=1000.0,
        default_boost_budget=75.0,
        approval_timeout_mins=60,
        slack_channel_id=settings.slack_channel_id,
    ),
    "notify-brand": BrandConfig(
        brand_id="notify-brand",
        brand_name="Notify-Only Brand",
        boost_mode=BoostMode.NOTIFY_ONLY,
        score_threshold=1.5,
        monthly_budget_cap=0.0,
        default_boost_budget=0.0,
        approval_timeout_mins=60,
        slack_channel_id=settings.slack_channel_id,
    ),
}


def get_brand_config(brand_id: str) -> BrandConfig:
    return BRAND_REGISTRY.get(
        brand_id,
        BrandConfig(brand_id=brand_id, brand_name=f"Unknown ({brand_id})"),
    )
