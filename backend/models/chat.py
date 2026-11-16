"""Schemas for the /chat route."""

from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat form submitted by the frontend."""

    story_id: str = Field(..., min_length=1, description="Story to ask about")
    question: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    citations: List[str]
    confidence: float
