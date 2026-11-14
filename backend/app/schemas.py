from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Platform = Literal["instagram", "tiktok", "x"]


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict


class ContentCreate(BaseModel):
    title: str = Field(min_length=2, max_length=140)
    source_notes: str = Field(min_length=3, max_length=4000)
    media_id: int | None = None
    platforms: list[Platform] = Field(min_length=1)


class PostUpdate(BaseModel):
    caption: str = Field(min_length=1, max_length=2200)
    hashtags: str = Field(default="", max_length=500)


class ScheduleRequest(BaseModel):
    scheduled_at: datetime

