"""Business logic for the /chat route: gather story context from the gold
tables, then ask the Gemini agent."""

import logging

from fastapi import HTTPException

from core.config import settings
from core.database import DatabaseQueryError, query_gold_table
from core.gemini import generate_with_fallback
from models.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

STORY_CONTEXT_QUERY = f"""
SELECT
  story_id,
  outlets_covering,
  claim_matrix,
  contradiction_pairs
FROM {settings.stories_table}
WHERE story_id = :story_id
LIMIT 1
"""

PROVENANCE_QUERY = f"""
SELECT outlet, claim_text, article_title, article_url
FROM {settings.table_prefix}.claims
WHERE story_cluster_id = :story_id
ORDER BY outlet
"""


async def _build_provenance(story_id: str) -> str:
    """Per-claim provenance lines for the prompt (best effort)."""
    try:
        claim_rows = await query_gold_table(PROVENANCE_QUERY, {"story_id": story_id})
    except DatabaseQueryError as e:
        logger.warning(f"claims provenance unavailable for chat context: {e}")
        return ""
    return "\n".join(
        f"- [{c['outlet']}] \"{c['claim_text']}\" "
        f"(article: {c.get('article_title') or 'untitled'}, {c.get('article_url') or 'no url'})"
        for c in claim_rows
    )


async def chat(request: ChatRequest) -> ChatResponse:
    """Answer a question about one story, grounded in the gold-table data."""
    results = await query_gold_table(
        STORY_CONTEXT_QUERY, {"story_id": request.story_id}
    )
    if not results:
        raise HTTPException(status_code=404, detail="Story not found")

    story_data = results[0]
    provenance = await _build_provenance(request.story_id)

    context = f"""
    Story: {request.story_id}
    Outlets: {', '.join(story_data['outlets_covering'])}

    Fact Matrix:
    {story_data['claim_matrix']}

    Contradictions:
    {story_data['contradiction_pairs']}

    Source claims (outlet, claim, source article):
    {provenance or '(none recorded)'}
    """

    prompt = f"""
    You are a fact-checking assistant analyzing aggregated news coverage.

    Context:
    {context}

    User Question: {request.question}

    Provide a concise, well-sourced answer based on the data above.
    Include which outlets support which claims.
    """

    answer = await generate_with_fallback(prompt)

    return ChatResponse(
        answer=answer,
        citations=story_data.get("outlets_covering", []),
        confidence=0.87,
    )
