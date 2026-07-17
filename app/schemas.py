import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class URLCreate(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None

    @field_validator("original_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 4 or len(v) > 50:
                raise ValueError("Custom alias must be between 4 and 50 characters")
            if not v.isalnum():
                raise ValueError("Custom alias must be alphanumeric")
        return v


class URLResponse(BaseModel):
    id: int
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime.datetime
    access_count: int
    is_custom: bool

    model_config = {"from_attributes": True}


class AccessLogResponse(BaseModel):
    id: int
    short_code: str
    accessed_at: datetime.datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    model_config = {"from_attributes": True}


class URLStats(BaseModel):
    url: URLResponse
    total_accesses: int
    recent_accesses: list[AccessLogResponse]
