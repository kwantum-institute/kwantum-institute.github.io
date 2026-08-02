"""Parallel collectors for OpenAlex, Crossref, arXiv, and PubMed."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Optional
from urllib.parse import quote

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

USER_AGENT = "KwantumInstituteScienceSearch/1.0 (mailto:noreply@kwantuminstitute.com)"
TIMEOUT = httpx.Timeout(20.0, connect=8.0)


def _http_get(url: str, params: Optional[dict[str, Any]] = None) -> Any:
    """Perform a GET request and return parsed JSON or raw text."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    with httpx.Client(timeout=TIMEOUT, headers=headers, follow_redirects=True) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "json" in content_type:
            return response.json()
        return response.text


def _normalize_record(
    *,
    title: str,
    doi: Optional[str],
    year: Optional[int],
    authors: list[str],
    abstract: str,
    journal: str,
    url: str,
    citation_count: int,
    is_oa: bool,
    oa_url: Optional[str],
    is_retracted: bool,
    source: str,
    peer_reviewed: bool,
) -> dict[str, Any]:
    """Build a uniform paper record."""
    return {
        "title": title.strip() if title else "Untitled",
        "doi": (doi or "").lower().replace("https://doi.org/", "").strip() or None,
        "year": year,
        "authors": authors[:12],
        "abstract": abstract.strip() if abstract else "",
        "journal": journal or "",
        "url": url or (f"https://doi.org/{doi}" if doi else ""),
        "citation_count": int(citation_count or 0),
        "is_open_access": bool(is_oa),
        "oa_url": oa_url,
        "is_retracted": bool(is_retracted),
        "source": source,
        "peer_reviewed": peer_reviewed,
        "badges": [],
    }


def _keyword_query(structured: dict[str, Any]) -> str:
    """Convert boolean-ish query into space-separated keywords for OpenAlex/arXiv."""
    raw = structured.get("boolean_query") or ""
    concepts = structured.get("concepts") or []
    if concepts:
        return " ".join(str(c) for c in concepts[:6])
    cleaned = (
        raw.replace(" AND ", " ")
        .replace(" OR ", " ")
        .replace(" NOT ", " ")
        .replace("(", " ")
        .replace(")", " ")
    )
    return " ".join(cleaned.split())


def search_openalex(structured: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    """Query OpenAlex works endpoint."""
    year_range = structured["year_range"]
    query = _keyword_query(structured)
    filters = [
        f"from_publication_date:{year_range['min']}-01-01",
        f"to_publication_date:{year_range['max']}-12-31",
        "type:article|preprint|review",
    ]
    params = {
        "search": query,
        "filter": ",".join(filters),
        "per_page": limit,
        "sort": "relevance_score:desc",
    }
    email = getattr(settings, "SCIENCE_SEARCH_POLITE_EMAIL", "")
    if email:
        params["mailto"] = email

    data = _http_get("https://api.openalex.org/works", params=params)
    results: list[dict[str, Any]] = []
    for item in data.get("results", []):
        authorships = item.get("authorships") or []
        authors = [
            (a.get("author") or {}).get("display_name", "")
            for a in authorships
            if (a.get("author") or {}).get("display_name")
        ]
        primary = item.get("primary_location") or {}
        source = (primary.get("source") or {}).get("display_name") or ""
        abstract_inverted = item.get("abstract_inverted_index") or {}
        abstract = _rebuild_openalex_abstract(abstract_inverted)
        doi = item.get("doi")
        if doi:
            doi = doi.replace("https://doi.org/", "")
        oa = item.get("open_access") or {}
        results.append(
            _normalize_record(
                title=item.get("display_name") or "",
                doi=doi,
                year=item.get("publication_year"),
                authors=authors,
                abstract=abstract,
                journal=source,
                url=item.get("id") or "",
                citation_count=item.get("cited_by_count") or 0,
                is_oa=bool(oa.get("is_oa")),
                oa_url=oa.get("oa_url"),
                is_retracted=bool(item.get("is_retracted")),
                source="openalex",
                peer_reviewed=True,
            )
        )
    return results


def _rebuild_openalex_abstract(inverted: dict[str, list[int]]) -> str:
    """Rebuild abstract text from OpenAlex inverted index."""
    if not inverted:
        return ""
    positions: dict[int, str] = {}
    for word, idxs in inverted.items():
        for idx in idxs:
            positions[idx] = word
    if not positions:
        return ""
    return " ".join(positions[i] for i in sorted(positions))


def search_crossref(structured: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    """Query Crossref works endpoint."""
    year_range = structured["year_range"]
    params = {
        "query.bibliographic": structured["boolean_query"],
        "rows": limit,
        "filter": f"from-pub-date:{year_range['min']},until-pub-date:{year_range['max']},type:journal-article",
        "select": "DOI,title,author,published-print,published-online,container-title,abstract,is-referenced-by-count,URL,link",
    }
    email = getattr(settings, "SCIENCE_SEARCH_POLITE_EMAIL", "")
    headers_note = f"; mailto:{email}" if email else ""
    headers = {"User-Agent": f"{USER_AGENT}{headers_note}"}

    with httpx.Client(timeout=TIMEOUT, headers=headers, follow_redirects=True) as client:
        response = client.get("https://api.crossref.org/works", params=params)
        response.raise_for_status()
        data = response.json()

    results: list[dict[str, Any]] = []
    for item in (data.get("message") or {}).get("items", []):
        title_list = item.get("title") or [""]
        authors_raw = item.get("author") or []
        authors = [
            " ".join(filter(None, [a.get("given"), a.get("family")])).strip()
            for a in authors_raw
        ]
        authors = [a for a in authors if a]
        year = None
        for date_key in ("published-print", "published-online"):
            parts = ((item.get(date_key) or {}).get("date-parts") or [[]])[0]
            if parts:
                year = parts[0]
                break
        journal_list = item.get("container-title") or [""]
        abstract = item.get("abstract") or ""
        abstract = re_sub_html(abstract)
        oa_url = None
        for link in item.get("link") or []:
            if link.get("content-type") == "application/pdf":
                oa_url = link.get("URL")
                break
        results.append(
            _normalize_record(
                title=title_list[0],
                doi=item.get("DOI"),
                year=year,
                authors=authors,
                abstract=abstract,
                journal=journal_list[0] if journal_list else "",
                url=item.get("URL") or "",
                citation_count=item.get("is-referenced-by-count") or 0,
                is_oa=bool(oa_url),
                oa_url=oa_url,
                is_retracted=False,
                source="crossref",
                peer_reviewed=True,
            )
        )
    return results


def re_sub_html(text: str) -> str:
    """Strip simple HTML/jats tags from Crossref abstracts."""
    import re

    return re.sub(r"<[^>]+>", " ", text or "").strip()


def search_arxiv(structured: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    """Query arXiv Atom API."""
    query = _keyword_query(structured)
    search_query = "all:" + quote(query)
    url = (
        "https://export.arxiv.org/api/query"
        f"?search_query={search_query}&start=0&max_results={limit}&sortBy=relevance"
    )
    xml_text = _http_get(url)
    if not isinstance(xml_text, str):
        return []

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    root = ET.fromstring(xml_text)
    results: list[dict[str, Any]] = []
    year_min = structured["year_range"]["min"]
    year_max = structured["year_range"]["max"]

    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").replace("\n", " ").strip()
        abstract = (entry.findtext("atom:summary", default="", namespaces=ns) or "").replace("\n", " ").strip()
        published = entry.findtext("atom:published", default="", namespaces=ns) or ""
        year = int(published[:4]) if published[:4].isdigit() else None
        if year and (year < year_min or year > year_max):
            continue
        authors = [
            (a.findtext("atom:name", default="", namespaces=ns) or "").strip()
            for a in entry.findall("atom:author", ns)
        ]
        link = ""
        pdf = None
        for link_el in entry.findall("atom:link", ns):
            href = link_el.attrib.get("href", "")
            if link_el.attrib.get("type") == "application/pdf":
                pdf = href
            if link_el.attrib.get("rel") == "alternate":
                link = href
        doi_el = entry.find("arxiv:doi", ns)
        doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None
        results.append(
            _normalize_record(
                title=title,
                doi=doi,
                year=year,
                authors=authors,
                abstract=abstract,
                journal="arXiv",
                url=link,
                citation_count=0,
                is_oa=True,
                oa_url=pdf or link,
                is_retracted=False,
                source="arxiv",
                peer_reviewed=False,
            )
        )
    return results


def search_pubmed(structured: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    """Query PubMed E-utilities (esearch + esummary)."""
    term = structured["boolean_query"]
    year_range = structured["year_range"]
    search_params = {
        "db": "pubmed",
        "term": term,
        "retmax": limit,
        "retmode": "json",
        "datetype": "pdat",
        "mindate": str(year_range["min"]),
        "maxdate": str(year_range["max"]),
        "sort": "relevance",
    }
    search = _http_get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", search_params)
    ids = (search.get("esearchresult") or {}).get("idlist") or []
    if not ids:
        return []

    summary = _http_get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        {"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
    )
    result_map = summary.get("result") or {}
    results: list[dict[str, Any]] = []
    for pmid in ids:
        item = result_map.get(pmid) or {}
        if not item or pmid == "uids":
            continue
        authors = [a.get("name", "") for a in (item.get("authors") or []) if a.get("name")]
        pubdate = item.get("pubdate") or ""
        year = int(pubdate[:4]) if pubdate[:4].isdigit() else None
        articleids = item.get("articleids") or []
        doi = next((a.get("value") for a in articleids if a.get("idtype") == "doi"), None)
        results.append(
            _normalize_record(
                title=item.get("title") or "",
                doi=doi,
                year=year,
                authors=authors,
                abstract="",
                journal=item.get("fulljournalname") or item.get("source") or "",
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                citation_count=0,
                is_oa=False,
                oa_url=None,
                is_retracted="Retracted Publication" in (item.get("pubtype") or []),
                source="pubmed",
                peer_reviewed=True,
            )
        )
    return results


def fetch_by_doi(doi: str) -> list[dict[str, Any]]:
    """Resolve a single DOI via OpenAlex, with Crossref fallback."""
    try:
        data = _http_get(f"https://api.openalex.org/works/https://doi.org/{doi}")
        authorships = data.get("authorships") or []
        authors = [
            (a.get("author") or {}).get("display_name", "")
            for a in authorships
            if (a.get("author") or {}).get("display_name")
        ]
        primary = data.get("primary_location") or {}
        journal = (primary.get("source") or {}).get("display_name") or ""
        oa = data.get("open_access") or {}
        return [
            _normalize_record(
                title=data.get("display_name") or "",
                doi=doi,
                year=data.get("publication_year"),
                authors=authors,
                abstract=_rebuild_openalex_abstract(data.get("abstract_inverted_index") or {}),
                journal=journal,
                url=data.get("id") or f"https://doi.org/{doi}",
                citation_count=data.get("cited_by_count") or 0,
                is_oa=bool(oa.get("is_oa")),
                oa_url=oa.get("oa_url"),
                is_retracted=bool(data.get("is_retracted")),
                source="openalex",
                peer_reviewed=True,
            )
        ]
    except Exception:
        logger.exception("OpenAlex DOI lookup failed for %s", doi)

    try:
        data = _http_get(f"https://api.crossref.org/works/{doi}")
        item = data.get("message") or {}
        title_list = item.get("title") or [""]
        authors = [
            " ".join(filter(None, [a.get("given"), a.get("family")])).strip()
            for a in (item.get("author") or [])
        ]
        year = None
        parts = ((item.get("published-print") or item.get("published-online") or {}).get("date-parts") or [[]])[0]
        if parts:
            year = parts[0]
        return [
            _normalize_record(
                title=title_list[0],
                doi=doi,
                year=year,
                authors=[a for a in authors if a],
                abstract=re_sub_html(item.get("abstract") or ""),
                journal=((item.get("container-title") or [""])[0]),
                url=item.get("URL") or f"https://doi.org/{doi}",
                citation_count=item.get("is-referenced-by-count") or 0,
                is_oa=False,
                oa_url=None,
                is_retracted=False,
                source="crossref",
                peer_reviewed=True,
            )
        ]
    except Exception:
        logger.exception("Crossref DOI lookup failed for %s", doi)
        return []


def fetch_by_arxiv(arxiv_id: str) -> list[dict[str, Any]]:
    """Fetch a single arXiv record by ID."""
    url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    xml_text = _http_get(url)
    if not isinstance(xml_text, str):
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml_text)
    entry = root.find("atom:entry", ns)
    if entry is None:
        return []
    title = (entry.findtext("atom:title", default="", namespaces=ns) or "").replace("\n", " ").strip()
    abstract = (entry.findtext("atom:summary", default="", namespaces=ns) or "").replace("\n", " ").strip()
    published = entry.findtext("atom:published", default="", namespaces=ns) or ""
    year = int(published[:4]) if published[:4].isdigit() else None
    authors = [
        (a.findtext("atom:name", default="", namespaces=ns) or "").strip()
        for a in entry.findall("atom:author", ns)
    ]
    link = ""
    pdf = None
    for link_el in entry.findall("atom:link", ns):
        href = link_el.attrib.get("href", "")
        if link_el.attrib.get("type") == "application/pdf":
            pdf = href
        if link_el.attrib.get("rel") == "alternate":
            link = href
    return [
        _normalize_record(
            title=title,
            doi=None,
            year=year,
            authors=authors,
            abstract=abstract,
            journal="arXiv",
            url=link,
            citation_count=0,
            is_oa=True,
            oa_url=pdf or link,
            is_retracted=False,
            source="arxiv",
            peer_reviewed=False,
        )
    ]


def fetch_by_pmid(pmid: str) -> list[dict[str, Any]]:
    """Fetch a single PubMed record by PMID."""
    summary = _http_get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        {"db": "pubmed", "id": pmid, "retmode": "json"},
    )
    item = (summary.get("result") or {}).get(pmid) or {}
    if not item:
        return []
    authors = [a.get("name", "") for a in (item.get("authors") or []) if a.get("name")]
    pubdate = item.get("pubdate") or ""
    year = int(pubdate[:4]) if pubdate[:4].isdigit() else None
    doi = next(
        (a.get("value") for a in (item.get("articleids") or []) if a.get("idtype") == "doi"),
        None,
    )
    return [
        _normalize_record(
            title=item.get("title") or "",
            doi=doi,
            year=year,
            authors=authors,
            abstract="",
            journal=item.get("fulljournalname") or item.get("source") or "",
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            citation_count=0,
            is_oa=False,
            oa_url=None,
            is_retracted="Retracted Publication" in (item.get("pubtype") or []),
            source="pubmed",
            peer_reviewed=True,
        )
    ]


COLLECTORS: dict[str, Callable[[dict[str, Any], int], list[dict[str, Any]]]] = {
    "openalex": search_openalex,
    "crossref": search_crossref,
    "arxiv": search_arxiv,
    "pubmed": search_pubmed,
}


def collect_parallel(structured: dict[str, Any], per_source: int = 8) -> list[dict[str, Any]]:
    """
    Run configured bibliographic APIs concurrently.

    Args:
        structured: Rewritten query payload.
        per_source: Max results to request from each source.

    Returns:
        Concatenated raw records from all successful sources.
    """
    domains = structured.get("domains") or ["openalex", "crossref", "arxiv"]
    collected: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=min(4, len(domains))) as pool:
        futures = {
            pool.submit(COLLECTORS[domain], structured, per_source): domain
            for domain in domains
            if domain in COLLECTORS
        }
        for future in as_completed(futures):
            domain = futures[future]
            try:
                collected.extend(future.result())
            except Exception:
                logger.exception("Collector failed for domain=%s", domain)
    return collected
