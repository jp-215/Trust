"""Schemas for the /story/{story_id} route."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StoryRecord(BaseModel):
    """One row from `story_records` as returned by the story detail query."""

    story_id: str
    story_title: Optional[str] = None
    outlets_covering: List[str] = Field(default_factory=list)
    num_articles: int = 0
    claim_matrix: List[Dict[str, Any]] = Field(default_factory=list)
    contradiction_pairs: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None


class SynthesisRecord(BaseModel):
    """One row from `story_synthesis` (table may not exist yet)."""

    synthesized_truth: Optional[str] = None
    synthesis_metadata: Optional[Any] = None
    synthesized_at: Optional[datetime] = None


class StoryResponse(BaseModel):
    """Story detail payload consumed by the frontend story page."""

    story_id: str
    story_title: Optional[str] = None
    outlets_covering: List[str]
    num_articles: int
    claim_matrix: List[Dict[str, Any]]
    contradiction_pairs: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: Optional[str] = None
    synthesized_truth: Optional[str]
    confidence: Optional[float]
