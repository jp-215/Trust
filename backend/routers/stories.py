"""Route: /stories"""

from typing import List

from fastapi import APIRouter, Query

from handlers import stories_handler
from models.stories import StoryListItem

router = APIRouter(tags=["stories"])


@router.get("/stories", response_model=List[StoryListItem])
async def list_stories(
    limit: int = Query(10, ge=1, le=200, description="Max stories to return"),
) -> List[StoryListItem]:
    """List stories in the gold table."""
    return await stories_handler.list_stories(limit)
