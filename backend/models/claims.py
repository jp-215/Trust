"""Schemas for the /story/{story_id}/claims route."""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class ClaimRecord(BaseModel):
    """One row from the `claims` table: per-claim source provenance."""

    claim_id: Optional[str] = None
    outlet: Optional[str] = None
    claim_text: Optional[str] = None
    article_id: Optional[str] = None
    article_title: Optional[str] = None
    article_url: Optional[str] = None
    claim_type: Optional[str] = None
    entities: Optional[List[Any]] = None
    extraction_model: Optional[str] = None
    extracted_at: Optional[datetime] = None
    confidence: Optional[float] = None


ClaimsResponse = List[ClaimRecord]
