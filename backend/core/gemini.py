"""
Gemini client wrapper.

The client is created lazily at startup (the server still boots without a
key; chat requests then fail with `GeminiUnavailableError` → HTTP 503).
Generation is synchronous in google-genai, so it is offloaded to a worker
thread to keep routes async.
"""

import asyncio
import logging
from typing import Optional

from google.genai import client as genai_client
from google.genai import types as genai_types

from core.config import settings

logger = logging.getLogger(__name__)


class GeminiUnavailableError(Exception):
    """Raised when the Gemini agent is not configured or is overloaded."""


# Models to try in order — first is preferred, rest are fallbacks for 503/overload.
# lite second: it is rarely congested, so one failed primary attempt
# falls through to a model that almost always answers quickly.
GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]

_client: Optional[genai_client.Client] = None


def init_client() -> Optional[genai_client.Client]:
    """Create the shared Gemini client if an API key is configured."""
    global _client
    if _client is None and settings.gemini_configured:
        _client = genai_client.Client(
            api_key=settings.gemini_api_key,
            http_options=genai_types.HttpOptions(timeout=settings.gemini_timeout_ms),
        )
    return _client


def is_available() -> bool:
    return init_client() is not None


def _generate_sync(prompt: str):
    """Call Gemini, falling back to older flash models when one is overloaded."""
    client = init_client()
    last_error: Optional[Exception] = None
    for model in GEMINI_MODELS:
        try:
            return client.models.generate_content(model=model, contents=prompt)
        except Exception as e:
            logger.warning(f"Gemini model {model} failed ({e}); trying next fallback")
            last_error = e
    raise last_error


async def generate_with_fallback(prompt: str) -> str:
    """Generate text without blocking the event loop. Returns the answer text."""
    if not is_available():
        raise GeminiUnavailableError(
            "Gemini agent unavailable: set GEMINI_API_KEY in .env"
        )
    try:
        response = await asyncio.to_thread(_generate_sync, prompt)
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        msg = str(e)
        if "503" in msg or "UNAVAILABLE" in msg or "timed out" in msg.lower():
            raise GeminiUnavailableError(
                "Gemini is overloaded right now — please try again in a minute."
            ) from e
        raise
