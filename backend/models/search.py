"""Schemas for the /search route."""

from typing import List

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """One matching row from `story_records` for a keyword search."""

    story_id: str
    outlets_covering: List[str] = Field(default_factory=list)
