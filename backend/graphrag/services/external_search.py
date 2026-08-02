"""Local-first evidence providers for GraphRAG.

External paid search APIs are optional. Prefer LocalCorpusClient, which
reads brain.md, soul.md, and other project documents without network calls.
"""

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class LocalCorpusClient:
    """Search local project documents without any remote API.

    Scans Markdown and text files under the repository root and ranks them
    by simple keyword overlap. Suitable for offline KAG research.
    """

    def __init__(self, root: Path | None = None, extensions: tuple[str, ...] = (".md", ".txt")) -> None:
        """Initialize the local corpus client.

        Args:
            root: Repository root to scan. Defaults to the project root.
            extensions: File extensions to include.
        """
        self.root = root or REPO_ROOT
        self.extensions = extensions

    def _iter_documents(self) -> list[dict[str, Any]]:
        """Load local documents from disk."""
        documents: list[dict[str, Any]] = []
        skip_dirs = {".git", "node_modules", "dist", "__pycache__", ".venv", "venv", "checkpoints"}
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in skip_dirs for part in path.parts):
                continue
            if path.suffix.lower() not in self.extensions:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                logger.warning("Skipping unreadable file %s: %s", path, exc)
                continue
            documents.append(
                {
                    "id": str(path.relative_to(self.root)),
                    "url": path.as_uri(),
                    "title": path.name,
                    "snippet": text[:1000],
                    "text": text,
                    "source": "local",
                    "sensitivity_tag": "internal",
                    "route_hint": "LOCAL",
                }
            )
        return documents

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Rank local documents by keyword overlap with the query.

        Args:
            query: Search query.
            limit: Maximum number of results.

        Returns:
            Ranked list of local source dictionaries.
        """
        terms = {t.lower() for t in re.findall(r"[a-zA-Z0-9_-]+", query) if len(t) > 2}
        if not terms:
            return []

        scored: list[tuple[float, dict[str, Any]]] = []
        for doc in self._iter_documents():
            doc_terms = {t.lower() for t in re.findall(r"[a-zA-Z0-9_-]+", doc["text"])}
            overlap = len(terms & doc_terms)
            if overlap == 0:
                continue
            score = overlap / max(len(terms), 1)
            scored.append((score, {**doc, "score": round(score, 4)}))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored[:limit]]


class BraveSearchClient:
    """Optional Brave Search client. Disabled unless BRAVE_API_KEY is set."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1/llm/context"

    def search(self, query: str, count: int = 10) -> list[dict[str, Any]]:
        if not self.api_key:
            logger.info("Brave Search skipped: no BRAVE_API_KEY (using local corpus)")
            return []
        try:
            import httpx
        except ImportError:
            logger.warning("httpx not installed; cannot call Brave Search")
            return []

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params = {"q": query, "count": count, "context_threshold_mode": "balanced"}
        try:
            response = httpx.get(self.base_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
        except Exception as exc:
            logger.warning("Brave search failed: %s", exc)
            return []

        data = response.json()
        sources: list[dict[str, Any]] = []
        grounding = data.get("grounding", {})
        for key in ("sources", "results"):
            for item in grounding.get(key, []):
                sources.append(
                    {
                        "id": item.get("url", "brave-result"),
                        "url": item.get("url", ""),
                        "title": item.get("title", "Untitled"),
                        "snippet": item.get("snippet", item.get("content", "")),
                        "source": "brave",
                        "sensitivity_tag": "public",
                        "route_hint": "CLOUD",
                    }
                )
        return sources


class PerplexityClient:
    """Optional Perplexity client. Disabled unless PERPLEXITY_API_KEY is set."""

    def __init__(self, api_key: str | None = None, api_base: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("PERPLEXITY_API_KEY")
        self.api_base = api_base or "https://api.perplexity.ai"

    def search(self, query: str, preset: str = "medium") -> list[dict[str, Any]]:
        if not self.api_key:
            logger.info("Perplexity skipped: no PERPLEXITY_API_KEY (using local corpus)")
            return []
        try:
            import httpx
        except ImportError:
            logger.warning("httpx not installed; cannot call Perplexity")
            return []

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "Be concise and cite sources."},
                {"role": "user", "content": query},
            ],
            "preset": preset,
        }
        try:
            response = httpx.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
        except Exception as exc:
            logger.warning("Perplexity search failed: %s", exc)
            return []

        data = response.json()
        citations = data.get("citations", [])
        sources: list[dict[str, Any]] = []
        for citation in citations:
            sources.append(
                {
                    "id": citation if isinstance(citation, str) else citation.get("id", "perplexity"),
                    "url": citation if isinstance(citation, str) else citation.get("url", ""),
                    "title": "Perplexity citation",
                    "snippet": data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")[:500],
                    "source": "perplexity",
                    "sensitivity_tag": "public",
                    "route_hint": "CLOUD",
                }
            )
        return sources


class ConsensusClient:
    """Optional Consensus client. Disabled unless CONSENSUS_API_KEY is set."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("CONSENSUS_API_KEY")
        self.mcp_url = "https://mcp.consensus.app/mcp"

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if not self.api_key:
            logger.info("Consensus skipped: no CONSENSUS_API_KEY (using local corpus)")
            return []
        try:
            import httpx
        except ImportError:
            logger.warning("httpx not installed; cannot call Consensus")
            return []

        try:
            response = httpx.post(
                self.mcp_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"tool": "search", "params": {"query": query, "limit": limit}},
                timeout=60,
            )
            response.raise_for_status()
        except Exception as exc:
            logger.warning("Consensus search failed: %s", exc)
            return []

        data = response.json()
        papers = data.get("results", data.get("papers", []))
        sources: list[dict[str, Any]] = []
        for paper in papers:
            sources.append(
                {
                    "id": paper.get("id", "consensus"),
                    "url": paper.get("url", ""),
                    "title": paper.get("title", "Untitled paper"),
                    "snippet": paper.get("abstract", "")[:500],
                    "authors": paper.get("authors", []),
                    "source": "consensus",
                    "sensitivity_tag": "academic",
                    "route_hint": "HYBRID",
                }
            )
        return sources


class OperaClient:
    """Optional Opera Neon CLI. Disabled unless opera-browser-cli is installed."""

    def __init__(self, executable: str = "opera-browser-cli") -> None:
        self.executable = executable

    def research(self, query: str, mode: str = "local") -> list[dict[str, Any]]:
        try:
            result = subprocess.run(
                [self.executable, "research", query, "--type", mode],
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
        except FileNotFoundError:
            logger.info("Opera CLI not found; using local corpus only")
            return []
        except subprocess.TimeoutExpired:
            logger.warning("Opera research query timed out")
            return []

        if result.returncode != 0:
            logger.warning("Opera research failed: %s", result.stderr)
            return []

        return [
            {
                "id": "opera-research",
                "url": "",
                "title": "Opera Neon research summary",
                "snippet": result.stdout[:1000],
                "source": "opera",
                "sensitivity_tag": "local",
                "route_hint": "LOCAL",
            }
        ]
