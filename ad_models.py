# ad_models.py  — shared Pydantic output schemas for the advertising pipeline
from pydantic import BaseModel, ConfigDict


class CreativeBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")
    campaign_name: str
    tagline_concept: str
    core_brand_message: str
    visual_direction: str
    objectives: list[str]


class CampaignStrategy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_audience: str
    messaging_pillars: list[str]
    recommended_channels: list[str]
    campaign_hooks: list[str]


class AdCopy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hero_tagline: str
    instagram_caption: str
    video_script: str
    email_subject: str
    email_preview: str
    print_headline: str
    print_body: str


class ChannelAllocation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    channel: str
    percent_of_budget: int


class MediaPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total_budget_usd: int
    channel_allocations: list[ChannelAllocation]   # NOT dict[str, int]
    campaign_timeline_weeks: int
    kpis: list[str]
    launch_milestones: list[str]
