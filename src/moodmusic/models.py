from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Song(BaseModel):
    id: str
    title: str
    artist: str
    tags: list[str] = Field(default_factory=list)
    description: str


class RecommendRequest(BaseModel):
    mood_text: str = Field(min_length=1, description="Free-form mood description")
    k: int = Field(default=5, ge=1, le=20)


class RecommendHit(BaseModel):
    song: Song
    score: float = Field(ge=-1.0, le=1.0)


class RecommendResponse(BaseModel):
    model: str
    results: list[RecommendHit]


class ErrorResponse(BaseModel):
    error: Literal["invalid_request", "internal_error"]
    message: str
    details: dict[str, Any] | None = None
