"""Business logic for the /stories route."""

from typing import Any, Dict, List

from core.config import settings
from core.database import query_gold_table

STORIES_QUERY = f"""
SELECT
  story_id,
  story_title,
  outlets_covering,
  article_count as num_articles,
  created_at
FROM {settings.stories_table}
LIMIT {{limit}}
"""


async def list_stories(limit: int) -> List[Dict[str, Any]]:
    """List stories in the gold table."""
    # LIMIT cannot be bound as a named parameter on all warehouse versions;
    # `limit` is validated as a bounded int by the router, so inlining is safe.
    return await query_gold_table(STORIES_QUERY.format(limit=int(limit)))
