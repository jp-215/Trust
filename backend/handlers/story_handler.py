"""Business logic for the /story/{story_id} route."""

import logging

from fastapi import HTTPException

from core.config import settings
from core.database import DatabaseQueryError, query_gold_table
from models.story import StoryRecord, StoryResponse, SynthesisRecord

logger = logging.getLogger(__name__)

STORY_QUERY = f"""
SELECT
  story_id,
  story_title,
  outlets_covering,
  article_count as num_articles,
  claim_matrix,
  contradiction_pairs,
  created_at
FROM {settings.stories_table}
WHERE story_id = :story_id
LIMIT 1
"""

SYNTHESIS_QUERY = f"""
SELECT synthesized_truth, synthesis_metadata, synthesized_at
FROM {settings.table_prefix}.story_synthesis
WHERE story_id = :story_id
LIMIT 1
"""


async def get_story(story_id: str) -> StoryResponse:
    """Fetch one story from the gold table, plus its synthesis if present."""
    results = await query_gold_table(STORY_QUERY, {"story_id": story_id})
    if not results:
        raise HTTPException(status_code=404, detail=f"Story '{story_id}' not found")

    story = StoryRecord.model_validate(results[0])

    # Synthesis is optional — the table may not exist yet
    synthesis = None
    try:
        synthesis_results = await query_gold_table(
            SYNTHESIS_QUERY, {"story_id": story_id}
        )
        if synthesis_results:
            synthesis = SynthesisRecord.model_validate(synthesis_results[0])
    except DatabaseQueryError:
        logger.warning(
            "story_synthesis table unavailable; returning story without synthesis"
        )

    return StoryResponse(
        story_id=story.story_id,
        story_title=story.story_title,
        outlets_covering=story.outlets_covering,
        num_articles=story.num_articles,
        claim_matrix=story.claim_matrix,
        contradiction_pairs=story.contradiction_pairs or [],
        created_at=str(results[0]["created_at"]) if results[0].get("created_at") else None,
        synthesized_truth=synthesis.synthesized_truth if synthesis else None,
        confidence=0.87,  # TODO: Extract from metadata
    )
