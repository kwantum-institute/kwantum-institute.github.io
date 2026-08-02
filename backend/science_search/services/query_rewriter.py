"""LLM query rewriter powered by Gemma 4 31B Instruct (Gemini API)."""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a scientific literature search translator.
Convert the user's natural-language science question into structured JSON for bibliographic APIs.
Return ONLY valid JSON matching this schema (no markdown fences):
{
  "boolean_query": "string (keywords with AND/OR, suitable for OpenAlex/Crossref)",
  "mesh_terms": ["string"],
  "concepts": ["string"],
  "year_range": {"min": 2018, "max": 2026},
  "domains": ["openalex"|"crossref"|"arxiv"|"pubmed"]
}
Rules:
- Prefer precise scientific keywords over conversational phrasing.
- Prefer peer-reviewed academic literature domains.
- year_range.max must not exceed the current year.
- Do not invent paper titles or DOIs.
- Never answer the science question; only rewrite the query.
"""


def _default_year_range() -> dict[str, int]:
    """Return a conservative default publication window."""
    current_year = datetime.utcnow().year
    return {"min": current_year - 8, "max": current_year}


def heuristic_rewrite(query: str) -> dict[str, Any]:
    """
    Fallback rewriter when no Gemma API key is configured.

    Args:
        query: Raw natural-language query.

    Returns:
        Structured search JSON compatible with external collectors.
    """
    cleaned = re.sub(r"[^\w\s\-]", " ", query.lower())
    tokens = [t for t in cleaned.split() if len(t) > 2]
    stop = {
        "the", "and", "for", "with", "what", "how", "why", "does", "do",
        "are", "is", "of", "in", "on", "to", "a", "an", "about", "effect",
        "effects", "impact", "impacts", "please", "find", "papers", "study",
        "studies", "research", "latest", "recent",
    }
    keywords = [t for t in tokens if t not in stop][:8] or tokens[:5] or ["science"]
    boolean_query = " AND ".join(keywords[:5])
    year_range = _default_year_range()
    domains = ["openalex", "crossref", "arxiv"]
    if any(t in {"pubmed", "clinical", "medical", "disease", "drug"} for t in keywords):
        domains.append("pubmed")
    return {
        "boolean_query": boolean_query,
        "mesh_terms": keywords[:4],
        "concepts": keywords[:6],
        "year_range": year_range,
        "domains": domains,
        "rewriter": "heuristic",
    }


def _extract_json(text: str) -> dict[str, Any]:
    """Parse JSON from model output, tolerating markdown fences."""
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    else:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


def _normalize_structured(data: dict[str, Any], query: str) -> dict[str, Any]:
    """Clamp and fill required fields on model output."""
    year_range = data.get("year_range") or _default_year_range()
    current_year = datetime.utcnow().year
    min_year = int(year_range.get("min", current_year - 8))
    max_year = int(year_range.get("max", current_year))
    max_year = min(max_year, current_year)
    min_year = min(min_year, max_year)

    boolean_query = str(data.get("boolean_query") or "").strip()
    if not boolean_query:
        boolean_query = heuristic_rewrite(query)["boolean_query"]

    domains = data.get("domains") or ["openalex", "crossref", "arxiv"]
    allowed = {"openalex", "crossref", "arxiv", "pubmed"}
    domains = [d for d in domains if d in allowed] or ["openalex", "crossref"]

    return {
        "boolean_query": boolean_query,
        "mesh_terms": [str(x) for x in (data.get("mesh_terms") or [])][:12],
        "concepts": [str(x) for x in (data.get("concepts") or [])][:12],
        "year_range": {"min": min_year, "max": max_year},
        "domains": domains,
        "rewriter": "gemma-4-31b-it",
    }


def rewrite_query_with_gemma(query: str) -> dict[str, Any]:
    """
    Convert a natural-language query into structured search JSON via Gemma.

    Uses google-genai Client with model ``gemma-4-31b-it``. Falls back to a
    local heuristic rewriter when ``GEMINI_API_KEY`` is missing.

    Args:
        query: User's science question.

    Returns:
        Structured query dict for API collectors.
    """
    api_key = getattr(settings, "GEMINI_API_KEY", "") or ""
    if not api_key:
        logger.warning("GEMINI_API_KEY unset; using heuristic query rewriter")
        return heuristic_rewrite(query)

    model_name = getattr(settings, "GEMMA_MODEL_ID", "gemma-4-31b-it")
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,
                response_mime_type="application/json",
            ),
            contents=query,
        )
        text = (response.text or "").strip()
        if not text:
            raise ValueError("Empty Gemma response")
        parsed = _extract_json(text)
        return _normalize_structured(parsed, query)
    except Exception as exc:  # noqa: BLE001 — fall back safely for UX
        logger.exception("Gemma rewrite failed (%s); using heuristic fallback", exc)
        fallback = heuristic_rewrite(query)
        fallback["rewriter"] = "heuristic_fallback"
        fallback["rewriter_error"] = str(exc)
        return fallback


def rewrite_query(query: str) -> dict[str, Any]:
    """Public entry point for query rewriting."""
    return rewrite_query_with_gemma(query)
