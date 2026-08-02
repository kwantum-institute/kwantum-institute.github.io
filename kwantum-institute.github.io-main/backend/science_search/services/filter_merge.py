"""Normalize, deduplicate, filter, and badge scientific search results."""

from __future__ import annotations

from typing import Any


HIGHLY_CITED_THRESHOLD = 50


def _token_set(text: str) -> set[str]:
    """Lowercase token set used for lightweight relevance scoring."""
    return {t for t in "".join(ch if ch.isalnum() else " " for ch in (text or "").lower()).split() if len(t) > 2}


def _relevance_score(record: dict[str, Any], query_terms: set[str]) -> int:
    """Count overlapping tokens between query terms and title/abstract."""
    if not query_terms:
        return 0
    haystack = _token_set(f"{record.get('title', '')} {record.get('abstract', '')}")
    return len(query_terms & haystack)


def _attach_badges(record: dict[str, Any]) -> dict[str, Any]:
    """Derive UI badges from metadata fields."""
    badges: list[str] = []
    if record.get("peer_reviewed"):
        badges.append("Peer Reviewed")
    if record.get("is_open_access") or record.get("oa_url"):
        badges.append("Open Access PDF")
    if int(record.get("citation_count") or 0) >= HIGHLY_CITED_THRESHOLD:
        badges.append("Highly Cited")
    if record.get("is_retracted"):
        badges.append("Retracted")
    if record.get("source") == "arxiv" and not record.get("peer_reviewed"):
        badges.append("Preprint")
    record["badges"] = badges
    return record


def filter_and_merge(
    records: list[dict[str, Any]],
    *,
    require_doi: bool = False,
    drop_retracted: bool = True,
    limit: int = 12,
    query_hint: str = "",
) -> list[dict[str, Any]]:
    """
    Deduplicate by DOI/title, filter quality, and rank results.

    Args:
        records: Raw collector outputs.
        require_doi: When True, drop entries without DOIs (preprints may keep IDs).
        drop_retracted: Remove retracted works when True; otherwise flag them.
        limit: Max results to return after ranking.
        query_hint: Original or rewritten query used for relevance scoring.

    Returns:
        Cleaned, ranked paper list with badges.
    """
    by_doi: dict[str, dict[str, Any]] = {}
    no_doi: list[dict[str, Any]] = []
    query_terms = _token_set(query_hint)

    for raw in records:
        record = dict(raw)
        doi = (record.get("doi") or "").strip().lower()
        if record.get("is_retracted") and drop_retracted:
            continue
        if not record.get("title"):
            continue
        if require_doi and not doi and record.get("source") != "arxiv":
            continue

        if doi:
            existing = by_doi.get(doi)
            if existing is None:
                by_doi[doi] = record
            else:
                # Prefer richer abstract / higher citations / peer review
                if len(record.get("abstract") or "") > len(existing.get("abstract") or ""):
                    existing["abstract"] = record["abstract"]
                if int(record.get("citation_count") or 0) > int(existing.get("citation_count") or 0):
                    existing["citation_count"] = record["citation_count"]
                if record.get("peer_reviewed") and not existing.get("peer_reviewed"):
                    existing["peer_reviewed"] = True
                if record.get("is_open_access"):
                    existing["is_open_access"] = True
                    existing["oa_url"] = existing.get("oa_url") or record.get("oa_url")
                if record.get("is_retracted"):
                    existing["is_retracted"] = True
                sources = {existing.get("source"), record.get("source")}
                existing["sources"] = sorted(s for s in sources if s)
        else:
            no_doi.append(record)

    # Title-level dedupe for no-DOI items
    seen_titles: set[str] = set()
    unique_no_doi: list[dict[str, Any]] = []
    for record in no_doi:
        key = " ".join((record.get("title") or "").lower().split())
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique_no_doi.append(record)

    merged = list(by_doi.values()) + unique_no_doi
    merged.sort(
        key=lambda r: (
            _relevance_score(r, query_terms),
            0 if r.get("is_retracted") else 1,
            1 if r.get("peer_reviewed") else 0,
            int(r.get("citation_count") or 0),
            int(r.get("year") or 0),
        ),
        reverse=True,
    )

    # Soft relevance floor: keep items with at least one token overlap when possible
    if query_terms:
        relevant = [r for r in merged if _relevance_score(r, query_terms) > 0]
        if relevant:
            merged = relevant

    return [_attach_badges(r) for r in merged[:limit]]
