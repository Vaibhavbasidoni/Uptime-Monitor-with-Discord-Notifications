from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class WebsiteBase(BaseModel):
    url: HttpUrl
    name: Optional[str] = None
    check_interval_seconds: Optional[int] = 300
    expected_status_code: Optional[int] = 200

class WebsiteCreate(WebsiteBase):
    pass

class Website(WebsiteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class StatusCheckBase(BaseModel):
    status: str
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None

class StatusCheck(StatusCheckBase):
    id: int
    website_id: int
    status: str
    response_time_ms: Optional[float]
    error_message: Optional[str]
    checked_at: datetime
    last_status_change: Optional[datetime]

    class Config:
        from_attributes = True

class DiscordWebhookCreate(BaseModel):
    url: HttpUrl
    name: Optional[str] = None

class DiscordWebhook(DiscordWebhookCreate):
    id: int

    class Config:
        from_attributes = True 