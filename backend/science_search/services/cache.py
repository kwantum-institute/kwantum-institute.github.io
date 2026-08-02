"""Cache helpers for science search results."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Optional

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def _cache_key(query: str) -> str:
    """Build a stable cache key from a normalized query string."""
    normalized = " ".join(query.lower().split())
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"science_search:v1:{digest}"


def get_cached_results(query: str) -> Optional[dict[str, Any]]:
    """
    Return cached search payload when present.

    Args:
        query: Raw user query.

    Returns:
        Cached response dict, or None on miss.
    """
    key = _cache_key(query)
    payload = cache.get(key)
    if payload is None:
        return None
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            logger.warning("Corrupt cache payload for key %s", key)
            return None
    return payload


def set_cached_results(query: str, payload: dict[str, Any]) -> None:
    """
    Store a search payload with the configured TTL.

    Args:
        query: Raw user query.
        payload: Unified response body to cache.
    """
    ttl = int(getattr(settings, "SCIENCE_SEARCH_CACHE_TTL", 60 * 60 * 24))
    key = _cache_key(query)
    cache.set(key, payload, timeout=ttl)
