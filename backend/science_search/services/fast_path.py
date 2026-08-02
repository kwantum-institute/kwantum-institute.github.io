"""Fast-path detection for DOIs, PubMed IDs, and paper URLs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


DOI_RE = re.compile(
    r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b",
    re.IGNORECASE,
)
PMID_RE = re.compile(r"\b(?:PMID[:\s]*)?(\d{5,9})\b", re.IGNORECASE)
ARXIV_RE = re.compile(
    r"(?:arxiv\.org/(?:abs|pdf)/|arxiv:)?(\d{4}\.\d{4,5})(?:v\d+)?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FastPathMatch:
    """Structured fast-path identifier extracted from a raw query."""

    kind: str
    value: str


def detect_fast_path(query: str) -> Optional[FastPathMatch]:
    """
    Detect whether a query is a direct identifier that can skip the LLM.

    Args:
        query: Raw user search string.

    Returns:
        FastPathMatch when a DOI, PMID, arXiv ID, or known paper URL is found.
    """
    text = (query or "").strip()
    if not text:
        return None

    doi_match = DOI_RE.search(text)
    if doi_match:
        return FastPathMatch(kind="doi", value=doi_match.group(1).rstrip("."))

    if text.lower().startswith(("http://", "https://")):
        parsed = urlparse(text)
        host = (parsed.netloc or "").lower()
        path = parsed.path or ""

        if "doi.org" in host:
            doi = path.lstrip("/")
            if DOI_RE.search(doi):
                return FastPathMatch(kind="doi", value=doi)

        if "pubmed.ncbi.nlm.nih.gov" in host:
            pmid = path.strip("/").split("/")[0]
            if pmid.isdigit():
                return FastPathMatch(kind="pmid", value=pmid)

        arxiv_match = ARXIV_RE.search(text)
        if arxiv_match:
            return FastPathMatch(kind="arxiv", value=arxiv_match.group(1))

    arxiv_match = ARXIV_RE.search(text)
    if arxiv_match and ("arxiv" in text.lower() or re.fullmatch(r"\d{4}\.\d{4,5}", text)):
        return FastPathMatch(kind="arxiv", value=arxiv_match.group(1))

    pmid_match = PMID_RE.fullmatch(text) or (
        PMID_RE.search(text) if text.lower().startswith("pmid") else None
    )
    if pmid_match:
        return FastPathMatch(kind="pmid", value=pmid_match.group(1))

    return None
