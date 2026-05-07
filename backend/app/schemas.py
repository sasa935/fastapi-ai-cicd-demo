from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class LinkCreate(BaseModel):
    url: HttpUrl


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    original_url: str
    created_at: datetime
    short_url: str
    clicks: int


class DailyClick(BaseModel):
    date: str
    count: int


class LinkStats(BaseModel):
    id: int
    code: str
    total_clicks: int
    daily: list[DailyClick]
