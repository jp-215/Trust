"""Business logic for the /outlets route."""

from typing import List

from core.config import settings
from core.database import query_gold_table

OUTLETS_QUERY = f"""
SELECT DISTINCT outlet
FROM {settings.table_prefix}.raw_articles
ORDER BY outlet
"""


async def list_outlets() -> List[str]:
    """Unique outlets present in the raw articles table."""
    results = await query_gold_table(OUTLETS_QUERY)
    return [r["outlet"] for r in results]
