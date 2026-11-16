"""
Trust Backend — API Gateway

Single entry point that wires together the modular service layers:

    routers/   one module per route path (thin, async endpoint definitions)
    handlers/  business logic, one module per router
    models/    pydantic schemas (Databricks rows + frontend contracts)
    core/      configuration, Databricks access, Gemini client

Run with:  uvicorn main:app --reload
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core import gemini
from core.config import settings
from core.database import DatabaseQueryError
from core.gemini import GeminiUnavailableError
from routers import ALL_ROUTERS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("gateway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validate environment configuration at startup and warm up clients."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    if settings.databricks_configured:
        logger.info(f"Databricks configured (catalog: {settings.table_prefix})")
    else:
        logger.warning(
            "Databricks env vars missing (DATABRICKS_SERVER_HOSTNAME, "
            "DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN) — data routes will fail"
        )

    if gemini.is_available():
        logger.info("Gemini client initialized")
    else:
        logger.warning("GEMINI_API_KEY not set — /chat will return 503")

    yield
    logger.info("Shutting down gateway")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    """Attach a request id and log method, path, status, and latency."""
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} "
        f"({elapsed_ms:.0f}ms) [{request_id}]"
    )
    return response


@app.exception_handler(DatabaseQueryError)
async def database_error_handler(request: Request, exc: DatabaseQueryError):
    return JSONResponse(
        status_code=500, content={"detail": f"Database error: {exc}"}
    )


@app.exception_handler(GeminiUnavailableError)
async def gemini_unavailable_handler(request: Request, exc: GeminiUnavailableError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


# Mount every route module through the single gateway registry
for router in ALL_ROUTERS:
    app.include_router(router)


@app.get("/", tags=["gateway"])
async def root():
    """Gateway index: service metadata and route map."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "endpoints": {
            "/health": "Health check with dependency status",
            "/story/{story_id}": "Get story details (GET or POST)",
            "/story/{story_id}/claims": "Per-claim source provenance",
            "/chat": "Chat with Gemini agent (POST)",
            "/stories": "List all stories",
            "/outlets": "Get outlet list",
            "/search": "Search stories (GET or POST)",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
