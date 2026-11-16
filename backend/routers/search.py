"""Route: /search"""

from typing import List

from fastapi import APIRouter, Query

from handlers import search_handler
from models.search import SearchResult

router = APIRouter(tags=["search"])

QueryParam = Query(..., min_length=1, max_length=500, description="Search keyword")
LimitParam = Query(10, ge=1, le=100, description="Max results to return")


# POST kept for backwards compatibility: the frontend calls
# `api.post('/search', null, { params: { query, limit } })`.
@router.post("/search", response_model=List[SearchResult])
async def search_post(
    query: str = QueryParam, limit: int = LimitParam
) -> List[SearchResult]:
    """Search stories by keyword (legacy POST form)."""
    return await search_handler.search_stories(query, limit)


@router.get("/search", response_model=List[SearchResult])
async def search_get(
    query: str = QueryParam, limit: int = LimitParam
) -> List[SearchResult]:
    """Search stories by keyword."""
    return await search_handler.search_stories(query, limit)
