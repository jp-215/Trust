"""Route: /story/{story_id}"""

from fastapi import APIRouter, Path

from handlers import story_handler
from models.story import StoryResponse

router = APIRouter(tags=["stories"])

StoryId = Path(..., min_length=1, max_length=256, description="Story identifier")


@router.get("/story/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str = StoryId) -> StoryResponse:
    """Get one story's detail from the gold table."""
    return await story_handler.get_story(story_id)


# POST kept for backwards compatibility: the frontend fetches story detail
# with POST (axios `api.post('/story/{id}')`).
@router.post("/story/{story_id}", response_model=StoryResponse)
async def get_story_post(story_id: str = StoryId) -> StoryResponse:
    """Get one story's detail (legacy POST form of the same route)."""
    return await story_handler.get_story(story_id)
