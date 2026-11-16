"""Business logic for the /search route."""

from typing import Any, Dict, List

from core.config import settings
from core.database import query_gold_table

SEARCH_QUERY = f"""
SELECT DISTINCT story_id, outlets_covering
FROM {settings.stories_table}
WHERE lower(story_title) LIKE lower(:pattern) OR lower(story_id) LIKE lower(:pattern)
LIMIT {{limit}}
"""


async def search_stories(query: str, limit: int) -> List[Dict[str, Any]]:
    """Keyword search over story titles and ids."""
    return await query_gold_table(
        SEARCH_QUERY.format(limit=int(limit)), {"pattern": f"%{query}%"}
    )
