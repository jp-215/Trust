"""Route: /outlets"""

from typing import List

from fastapi import APIRouter

from handlers import outlets_handler

router = APIRouter(tags=["outlets"])


@router.get("/outlets", response_model=List[str])
async def get_outlets() -> List[str]:
    """Unique outlets present in the database."""
    return await outlets_handler.list_outlets()
