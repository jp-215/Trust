"""
Databricks / Unity Catalog access layer.

The databricks-sql-connector is synchronous, so every query is offloaded to a
worker thread with `asyncio.to_thread` — route handlers stay fully async and
the event loop is never blocked by a warehouse round-trip.

Handlers call `query_gold_table()` and receive plain lists of dicts; failures
raise `DatabaseQueryError`, which the gateway maps to an HTTP 500.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from databricks import sql

from core.config import settings

logger = logging.getLogger(__name__)


class DatabaseQueryError(Exception):
    """Raised when a Unity Catalog query fails."""


def _get_connection():
    return sql.connect(
        server_hostname=settings.databricks_server_hostname,
        http_path=settings.databricks_http_path,
        access_token=settings.databricks_token,
    )


def to_serializable(value: Any) -> Any:
    """Recursively convert databricks Row objects (nested structs/arrays)
    into plain dicts/lists so FastAPI can serialize them."""
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


def _run_query(query: str, params: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [
                {col: to_serializable(val) for col, val in zip(columns, row)}
                for row in rows
            ]


async def query_gold_table(
    query: str, params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Execute a (optionally parameterized) query against Unity Catalog
    without blocking the event loop."""
    try:
        return await asyncio.to_thread(_run_query, query, params)
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise DatabaseQueryError(str(e)) from e
