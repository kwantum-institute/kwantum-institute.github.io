"""End-to-end science search pipeline orchestration."""

from __future__ import annotations

import logging
from typing import Any

from .cache import get_cached_results, set_cached_results
from .collectors import (
    collect_parallel,
    fetch_by_arxiv,
    fetch_by_doi,
    fetch_by_pmid,
)
from .fast_path import detect_fast_path
from .filter_merge import filter_and_merge
from .query_rewriter import rewrite_query

logger = logging.getLogger(__name__)


def _plain_english_takeaway(abstract: str, title: str) -> str:
    """
    Produce a short non-LLM takeaway from the abstract opening.

    Deliberately avoids generative synthesis so the UI stays source-first.
    """
    text = (abstract or "").strip()
    if not text:
        return f"Source paper: {title}"
    sentence = text.split(". ")[0].strip()
    if not sentence.endswith("."):
        sentence += "."
    if len(sentence) > 220:
        sentence = sentence[:217].rstrip() + "..."
    return sentence


def run_search_pipeline(query: str, *, use_cache: bool = True) -> dict[str, Any]:
    """
    Execute the full search middleware pipeline.

    Steps:
        1. Fast-path DOI/PMID/arXiv bypass
        2. Redis/Django cache inspection
        3. Gemma query rewrite (or heuristic fallback)
        4. Parallel bibliographic API collection
        5. Deduplicate / retract / badge
        6. Attach plain-English excerpt takeaways + cache

    Args:
        query: Raw user question or identifier.
        use_cache: Whether to read/write the response cache.

    Returns:
        Unified JSON response for the frontend.
    """
    cleaned = (query or "").strip()
    if not cleaned:
        return {
            "success": False,
            "error": "Query is required.",
            "results": [],
        }

    if use_cache:
        cached = get_cached_results(cleaned)
        if cached is not None:
            cached = dict(cached)
            cached["cache_hit"] = True
            return cached

    fast = detect_fast_path(cleaned)
    structured: dict[str, Any] | None = None
    raw_records: list[dict[str, Any]] = []

    if fast is not None:
        logger.info("Fast-path %s=%s", fast.kind, fast.value)
        if fast.kind == "doi":
            raw_records = fetch_by_doi(fast.value)
        elif fast.kind == "pmid":
            raw_records = fetch_by_pmid(fast.value)
        elif fast.kind == "arxiv":
            raw_records = fetch_by_arxiv(fast.value)
        structured = {
            "boolean_query": fast.value,
            "mesh_terms": [],
            "concepts": [],
            "year_range": {},
            "domains": [fast.kind],
            "rewriter": "fast_path",
        }
    else:
        structured = rewrite_query(cleaned)
        raw_records = collect_parallel(structured)

    hint = " ".join(
        [
            cleaned,
            (structured or {}).get("boolean_query", ""),
            " ".join((structured or {}).get("concepts") or []),
        ]
    )
    results = filter_and_merge(
        raw_records,
        require_doi=False,
        drop_retracted=True,
        limit=12,
        query_hint=hint,
    )
    for item in results:
        item["tldr"] = _plain_english_takeaway(item.get("abstract", ""), item.get("title", ""))

    payload: dict[str, Any] = {
        "success": True,
        "query": cleaned,
        "structured_query": structured,
        "result_count": len(results),
        "results": results,
        "cache_hit": False,
        "note": (
            "Results are bibliographic sources only. "
            "No AI-generated answers are included."
        ),
    }

    if use_cache:
        set_cached_results(cleaned, payload)

    return payload
