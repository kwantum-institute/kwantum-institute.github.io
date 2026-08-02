"""Chunking and embedding service using BAAI/bge-small-en-v1.5."""

import hashlib
import logging
from typing import Iterable

logger = logging.getLogger(__name__)

CHUNK_SIZE = 384
CHUNK_OVERLAP = 48
MAX_SEQ_LENGTH = 512
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


class EmbeddingService:
    """Embed text chunks with BAAI/bge-small-en-v1.5.

    The model is loaded lazily so the module can be imported without the full
    transformer stack in memory.
    """

    _model: object | None = None
    _tokenizer: object | None = None

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        """Initialize the embedding service.

        Args:
            model_name: Hugging Face model identifier for the embedding model.
        """
        self.model_name = model_name

    def _load(self) -> None:
        """Load the embedding model and tokenizer on first use."""
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            logger.error("sentence-transformers is not installed")
            raise RuntimeError("Install sentence-transformers to use embeddings") from exc

        logger.info("Loading embedding model: %s", self.model_name)
        self._model = SentenceTransformer(self.model_name)

    def chunk_text(
        self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
    ) -> list[dict[str, object]]:
        """Split text into overlapping token-sized chunks.

        Args:
            text: Source text to chunk.
            chunk_size: Target chunk length in tokens.
            overlap: Number of tokens shared between adjacent chunks.

        Returns:
            A list of chunk dictionaries with text, start_index, and end_index.
        """
        if not text:
            return []

        words = text.split()
        step = max(1, chunk_size - overlap)
        chunks: list[dict[str, object]] = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            chunks.append(
                {
                    "text": chunk_text,
                    "start_index": start,
                    "end_index": end,
                    "content_hash": hashlib.sha256(chunk_text.encode()).hexdigest()[:16],
                }
            )
            if end == len(words):
                break
            start += step
        return chunks

    def embed(
        self, texts: list[str], *, is_query: bool = False
    ) -> "numpy.ndarray":
        """Embed a list of texts.

        Args:
            texts: Texts to embed.
            is_query: Whether the texts are short queries. If True, the BGE
                query instruction is prepended.

        Returns:
            A NumPy array of shape (len(texts), embedding_dim) with normalized
            embeddings.
        """
        import numpy as np

        self._load()
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)

        if is_query:
            texts = [f"{QUERY_INSTRUCTION}{t}" for t in texts]

        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return np.asarray(embeddings, dtype=np.float32)

    def embed_chunks(
        self, chunks: Iterable[dict[str, object]]
    ) -> list[dict[str, object]]:
        """Embed a list of chunk dictionaries in batches.

        Args:
            chunks: Chunk dictionaries as produced by chunk_text.

        Returns:
            The same chunk dictionaries with an added "embedding" key.
        """
        chunk_list = list(chunks)
        if not chunk_list:
            return []

        texts = [c["text"] for c in chunk_list]
        embeddings = self.embed(texts, is_query=False)
        for chunk, embedding in zip(chunk_list, embeddings):
            chunk["embedding"] = embedding.tolist()
        return chunk_list
