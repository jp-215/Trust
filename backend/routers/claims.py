"""Route: /story/{story_id}/claims"""

from typing import List

from fastapi import APIRouter, Path

from handlers import claims_handler
from models.claims import ClaimRecord

router = APIRouter(tags=["stories"])


@router.get("/story/{story_id}/claims", response_model=List[ClaimRecord])
async def get_story_claims(
    story_id: str = Path(..., min_length=1, max_length=256),
) -> List[ClaimRecord]:
    """Per-claim provenance for one story: source articles, outlets,
    entities, and extraction metadata."""
    return await claims_handler.get_story_claims(story_id)
