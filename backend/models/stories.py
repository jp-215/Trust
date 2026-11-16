"""Schemas for the /stories route."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StoryListItem(BaseModel):
    """One row from `story_records` as returned by the story list query."""

    story_id: str
    story_title: Optional[str] = None
    outlets_covering: List[str] = Field(default_factory=list)
    num_articles: int = 0
    created_at: Optional[datetime] = None
