"""Compressed vector sidecar index for asymmetric retrieval.

Implements the architecture-skill asymmetric retrieval principle:
- canonical content + metadata live in the primary store
- compressed vectors live in a sidecar index
- queries are scored directly against compressed vectors
- sensitivity/route metadata is returned with each result
"""

import logging
import math
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CompressionConfig:
    """Configuration for compressed sidecar vectors."""

    bit_width: int = 8
    embedding_dim: int = 384
    seed: int = 42
    device: str = "cpu"


class CompressedVectorSidecar:
    """Store and search quantized embeddings.

    Uses scalar quantization to a configurable bit-width. The query vector is
    kept in full precision while index vectors are quantized, giving asymmetric
    scoring speed without a full decompression loop.
    """

    def __init__(self, config: CompressionConfig | None = None) -> None:
        """Initialize the compressed sidecar index.

        Args:
            config: Compression settings. Defaults to 8-bit, 384-dim, CPU.
        """
        self.config = config or CompressionConfig()
        self._entries: dict[str, dict[str, Any]] = {}

    def _quantize(self, vector: list[float]) -> list[int]:
        """Quantize a full-precision vector to unsigned integers.

        Args:
            vector: Full-precision embedding vector.

        Returns:
            Quantized values as integers.
        """
        levels = 2**self.config.bit_width - 1
        quantized: list[int] = []
        for value in vector:
            clipped = max(-1.0, min(1.0, value))
            quantized.append(round((clipped + 1.0) / 2.0 * levels))
        return quantized

    def _dequantize_for_reference(self, quantized: list[int]) -> list[float]:
        """Dequantize a vector for reference comparison only.

        Scoring itself uses the quantized form to avoid decompression.
        """
        levels = 2**self.config.bit_width - 1
        return [2.0 * (q / levels) - 1.0 for q in quantized]

    @staticmethod
    def _asymmetric_score(query: list[float], quantized: list[int], levels: int) -> float:
        """Score a full-precision query against a quantized vector.

        The query is not quantized; only the indexed vector is compressed.
        """
        score = 0.0
        for q, code in zip(query, quantized):
            reconstructed = 2.0 * (code / levels) - 1.0
            score += q * reconstructed
        return score

    def add(
        self,
        chunk_id: str,
        vector: list[float],
        source_id: str,
        text: str,
        sensitivity_tag: str = "public",
        route_hint: str = "LOCAL",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a chunk to the compressed sidecar index.

        Args:
            chunk_id: Unique chunk identifier.
            vector: Full-precision embedding vector.
            source_id: Source document identifier.
            text: Chunk text (canonical content stays in primary store too).
            sensitivity_tag: Sensitivity label for policy enforcement.
            route_hint: Preferred routing target.
            metadata: Optional additional metadata.
        """
        quantized = self._quantize(vector)
        self._entries[chunk_id] = {
            "chunk_id": chunk_id,
            "quantized": quantized,
            "source_id": source_id,
            "text": text,
            "sensitivity_tag": sensitivity_tag,
            "route_hint": route_hint,
            "metadata": metadata or {},
        }

    def search(
        self, query_vector: list[float], top_k: int = 10
    ) -> list[dict[str, Any]]:
        """Score a full-precision query directly against compressed vectors.

        Args:
            query_vector: Full-precision query embedding.
            top_k: Number of top results to return.

        Returns:
            Scored chunks with source metadata, sensitivity tags, and route hints.
        """
        levels = 2**self.config.bit_width - 1
        scores: list[tuple[float, str]] = []
        for chunk_id, entry in self._entries.items():
            score = self._asymmetric_score(query_vector, entry["quantized"], levels)
            scores.append((score, chunk_id))

        scores.sort(reverse=True)
        results = []
        for score, chunk_id in scores[:top_k]:
            entry = self._entries[chunk_id]
            results.append(
                {
                    "chunk_id": chunk_id,
                    "source_id": entry["source_id"],
                    "text": entry["text"],
                    "score": round(score, 4),
                    "sensitivity_tag": entry["sensitivity_tag"],
                    "route_hint": entry["route_hint"],
                    "metadata": entry["metadata"],
                }
            )
        return results

    def remove(self, chunk_id: str) -> None:
        """Remove a chunk from the sidecar index."""
        self._entries.pop(chunk_id, None)

    def stats(self) -> dict[str, Any]:
        """Return index statistics."""
        return {
            "entries": len(self._entries),
            "bit_width": self.config.bit_width,
            "embedding_dim": self.config.embedding_dim,
            "device": self.config.device,
            "estimated_bytes": len(self._entries)
            * self.config.embedding_dim
            * (self.config.bit_width // 8),
        }

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two full-precision vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
