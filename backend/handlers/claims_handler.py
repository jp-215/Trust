"""Business logic for the /story/{story_id}/claims route."""

from typing import Any, Dict, List

from core.config import settings
from core.database import query_gold_table

CLAIMS_QUERY = f"""
SELECT
  claim_id,
  outlet,
  claim_text,
  article_id,
  article_title,
  article_url,
  claim_type,
  entities,
  extraction_model,
  extracted_at,
  confidence
FROM {settings.table_prefix}.claims
WHERE story_cluster_id = :story_id
ORDER BY outlet, extracted_at
"""


async def get_story_claims(story_id: str) -> List[Dict[str, Any]]:
    """Per-claim provenance from the claims table: source articles,
    outlets, entities, and extraction metadata for one story."""
    return await query_gold_table(CLAIMS_QUERY, {"story_id": story_id})
