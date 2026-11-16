"""
Trust Backend API - FastAPI
Serves queries to Unity Catalog and orchestrates Gemini agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
from pathlib import Path
from databricks import sql
from google.genai import client as genai_client
from google.genai import types as genai_types
from dotenv import load_dotenv

# Load .env from backend/ if present, falling back to the project root .env
load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Trust Backend", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_SERVER_HOSTNAME")
DATABRICKS_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

# Gemini configuration (lazy: server still starts without a key; /chat returns 503)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = (
    genai_client.Client(
        api_key=GEMINI_API_KEY,
        http_options=genai_types.HttpOptions(
            # 20s per model: with 4 fallback models the whole chain stays
            # under ~80s, inside the frontend's 120s request budget.
            timeout=20_000,
        ),
    )
    if GEMINI_API_KEY
    else None
)

# Models to try in order — first is preferred, rest are fallbacks for 503/overload
# lite second: it is rarely congested, so one failed primary attempt
# falls through to a model that almost always answers quickly
GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]


def generate_with_fallback(prompt: str):
    """Call Gemini, falling back to older flash models when one is overloaded."""
    last_error = None
    for model in GEMINI_MODELS:
        try:
            return gemini_client.models.generate_content(model=model, contents=prompt)
        except Exception as e:
            logger.warning(f"Gemini model {model} failed ({e}); trying next fallback")
            last_error = e
    raise last_error

# Models
class StoryRequest(BaseModel):
    story_id: str

class ChatRequest(BaseModel):
    story_id: str
    question: str

class StoryResponse(BaseModel):
    story_id: str
    story_title: Optional[str] = None
    outlets_covering: List[str]
    num_articles: int
    claim_matrix: List[dict]
    contradiction_pairs: List[dict] = []
    created_at: Optional[str] = None
    synthesized_truth: Optional[str]
    confidence: Optional[float]

class ChatResponse(BaseModel):
    answer: str
    citations: List[str]
    confidence: float

# Database connection pool
def get_db_connection():
    return sql.connect(
        server_hostname=DATABRICKS_HOST,
        http_path=DATABRICKS_PATH,
        access_token=DATABRICKS_TOKEN,
    )

# Helper: recursively convert databricks Row objects (nested structs/arrays)
# into plain dicts/lists so FastAPI can serialize them
def to_serializable(value):
    if hasattr(value, "asDict"):  # databricks.sql.types.Row
        return {k: to_serializable(v) for k, v in value.asDict().items()}
    if isinstance(value, dict):
        return {k: to_serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_serializable(v) for v in value]
    if isinstance(value, (str, bytes, int, float, bool)) or value is None:
        return value
    if hasattr(value, "tolist"):  # numpy arrays / numpy scalars (Arrow results)
        return to_serializable(value.tolist())
    if hasattr(value, "item"):  # remaining numpy scalar types
        return value.item()
    return value


# Helper: Query Unity Catalog
def query_gold_table(query: str, params: Optional[dict] = None) -> List[dict]:
    """Execute (optionally parameterized) query against Unity Catalog"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [
                    {col: to_serializable(val) for col, val in zip(columns, row)}
                    for row in rows
                ]
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Endpoints
@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "service": "Trust Backend"}

@app.post("/story/{story_id}", response_model=StoryResponse)
def get_story(story_id: str):
    """Get story from gold table"""

    query = f"""
    SELECT
      story_id,
      story_title,
      outlets_covering,
      size(source_article_ids) as num_articles,
      claim_matrix,
      contradiction_pairs,
      created_at
    FROM workspace.trust_dev.story_records
    WHERE story_id = '{story_id}'
    LIMIT 1
    """

    results = query_gold_table(query)

    if not results:
        raise HTTPException(status_code=404, detail=f"Story '{story_id}' not found")

    story = results[0]

    # Get synthesis if exists
    synthesis_query = f"""
    SELECT synthesized_truth, synthesis_metadata, synthesized_at
    FROM workspace.trust_dev.story_synthesis
    WHERE story_id = '{story_id}'
    LIMIT 1
    """

    # Synthesis is optional — the table may not exist yet
    try:
        synthesis_results = query_gold_table(synthesis_query)
        synthesis = synthesis_results[0] if synthesis_results else None
    except HTTPException:
        logger.warning("story_synthesis table unavailable; returning story without synthesis")
        synthesis = None

    return StoryResponse(
        story_id=story["story_id"],
        story_title=story.get("story_title"),
        outlets_covering=story["outlets_covering"],
        num_articles=story["num_articles"],
        claim_matrix=story["claim_matrix"],
        contradiction_pairs=story.get("contradiction_pairs") or [],
        created_at=str(story["created_at"]) if story.get("created_at") else None,
        synthesized_truth=synthesis["synthesized_truth"] if synthesis else None,
        confidence=0.87,  # TODO: Extract from metadata
    )

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat interface - powered by Gemini agent"""

    if gemini_client is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini agent unavailable: set GEMINI_API_KEY in .env",
        )

    try:
        # Step 1: Query gold table
        query = f"""
        SELECT
          story_id,
          outlets_covering,
          claim_matrix,
          contradiction_pairs,
          source_article_ids
        FROM workspace.trust_dev.story_records
        WHERE story_id = '{request.story_id}'
        LIMIT 1
        """

        results = query_gold_table(query)
        if not results:
            raise HTTPException(status_code=404, detail="Story not found")

        story_data = results[0]

        # Step 2: Per-claim provenance from the claims table (best effort)
        provenance = ""
        try:
            claim_rows = query_gold_table(
                """
                SELECT outlet, claim_text, article_title, article_url
                FROM workspace.trust_dev.claims
                WHERE story_cluster_id = :story_id
                ORDER BY outlet
                """,
                {"story_id": request.story_id},
            )
            provenance = "\n".join(
                f"- [{c['outlet']}] \"{c['claim_text']}\" "
                f"(article: {c.get('article_title') or 'untitled'}, {c.get('article_url') or 'no url'})"
                for c in claim_rows
            )
        except Exception as e:
            logger.warning(f"claims provenance unavailable for chat context: {e}")

        # Step 3: Build context for Gemini
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

        # Step 3: Call Gemini agent
        prompt = f"""
        You are a fact-checking assistant analyzing aggregated news coverage.

        Context:
        {context}

        User Question: {request.question}

        Provide a concise, well-sourced answer based on the data above.
        Include which outlets support which claims.
        """

        response = generate_with_fallback(prompt)

        answer = response.candidates[0].content.parts[0].text

        # Step 4: Extract citations from story data
        citations = story_data.get("outlets_covering", [])

        return ChatResponse(
            answer=answer,
            citations=citations,
            confidence=0.87,
        )

    except HTTPException:
        raise  # preserve 404s etc.
    except Exception as e:
        logger.error(f"Chat error: {e}")
        msg = str(e)
        if "503" in msg or "UNAVAILABLE" in msg or "timed out" in msg.lower():
            raise HTTPException(
                status_code=503,
                detail="Gemini is overloaded right now — please try again in a minute.",
            )
        raise HTTPException(status_code=500, detail=f"Chat error: {msg}")

@app.get("/story/{story_id}/claims")
def get_story_claims(story_id: str):
    """Per-claim provenance from the claims table: source articles,
    outlets, entities, and extraction metadata for one story."""

    query = """
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
    FROM workspace.trust_dev.claims
    WHERE story_cluster_id = :story_id
    ORDER BY outlet, extracted_at
    """

    return query_gold_table(query, {"story_id": story_id})


@app.get("/stories")
def list_stories(limit: int = 10):
    """List all stories in gold table"""

    query = f"""
    SELECT
      story_id,
      story_title,
      outlets_covering,
      size(source_article_ids) as num_articles,
      created_at
    FROM workspace.trust_dev.story_records
    LIMIT {limit}
    """

    return query_gold_table(query)

@app.get("/outlets")
def get_outlets():
    """Get unique outlets in database"""

    query = """
    SELECT DISTINCT outlet
    FROM workspace.trust_dev.raw_articles
    ORDER BY outlet
    """

    results = query_gold_table(query)
    return [r["outlet"] for r in results]

@app.post("/search")
def search(query: str, limit: int = 10):
    """Search stories by keyword"""

    search_query = f"""
    SELECT DISTINCT story_id, outlets_covering
    FROM workspace.trust_dev.story_records
    WHERE lower(story_title) LIKE lower(:pattern) OR lower(story_id) LIKE lower(:pattern)
    LIMIT {int(limit)}
    """

    return query_gold_table(search_query, {"pattern": f"%{query}%"})

# Root
@app.get("/")
async def root():
    """API info"""
    return {
        "name": "Trust Backend",
        "version": "0.1.0",
        "description": "Fact-checker backend with Gemini agent integration",
        "endpoints": {
            "/health": "Health check",
            "/story/{story_id}": "Get story details",
            "/chat": "Chat with Gemini agent",
            "/stories": "List all stories",
            "/outlets": "Get outlet list",
            "/search": "Search stories",
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
