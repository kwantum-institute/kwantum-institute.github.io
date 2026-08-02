"""KAG-style extraction, reasoning, and evidence-weighted consensus engine."""

import hashlib
import json
import logging
from typing import Any

from ..serializers import GraphEdgeSerializer, GraphNodeSerializer, ProvenanceSerializer
from .compressed_index import CompressedVectorSidecar, CompressionConfig
from .embedding import EmbeddingService
from .hooks import CascadeRoutingHook, ConflictDetectionHook, HookChain, HookEvent, PolicyFilterHook
from .llm import EXTRACTION_PRESET, HYPOTHESIS_PRESET, QwenClient
from .external_search import LocalCorpusClient, BraveSearchClient, ConsensusClient, PerplexityClient
from .tuning import ManualTuner, TuningConfig

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are a precise knowledge-graph extraction engine.
Read the provided context and produce a JSON object with exactly two keys:
"nodes" and "edges".

Each node must have:
- id: lowercase slug with only letters, numbers, hyphens, underscores
- label: human-readable name (max 512 chars)
- node_type: one of concept, person, organization, technology, event, paper, question
- description: short plain-text definition
- confidence: a number between 0 and 1

Each edge must have:
- id: lowercase slug
- source_id: id of an existing or newly created node
- target_id: id of an existing or newly created node
- edge_type: one of relates_to, depends_on, enables, contradicts, cited_by, part_of, solves
- label: short relationship label (optional)
- confidence: a number between 0 and 1

Do not include markdown, explanations, or anything outside the JSON object.
"""

HYPOTHESIS_SYSTEM_PROMPT = """You are a creative research assistant.
Given the context and current graph, generate alternate search queries and
relationship hypotheses that might be missing from the graph.

Return a JSON object with exactly two keys:
- "queries": list of alternate search queries (strings)
- "hypotheses": list of objects, each with source_id, target_id, edge_type,
  label, and rationale

Do not include markdown or explanations outside the JSON object.
"""


class KAGEngine:
    """Extract and validate graph candidates using dual Qwen sampling.

    Integrates architecture-skill components: asymmetric compressed retrieval,
    hook-chain routing/policy enforcement, and manual fine-tuning config.
    """

    def __init__(
        self,
        llm: QwenClient | None = None,
        embedder: EmbeddingService | None = None,
        local_corpus: LocalCorpusClient | None = None,
        brave: BraveSearchClient | None = None,
        perplexity: PerplexityClient | None = None,
        consensus: ConsensusClient | None = None,
        compressed_index: CompressedVectorSidecar | None = None,
        hook_chain: HookChain | None = None,
        tuning_config: TuningConfig | None = None,
    ) -> None:
        """Initialize the KAG engine.

        Args:
            llm: Qwen orchestration client (local by default).
            embedder: BGE embedding service (local by default).
            local_corpus: Offline corpus searcher (preferred evidence source).
            brave: Optional Brave Search client (requires API key).
            perplexity: Optional Perplexity client (requires API key).
            consensus: Optional Consensus client (requires API key).
            compressed_index: Asymmetric compressed sidecar index.
            hook_chain: Hook chain for routing and policy enforcement.
            tuning_config: Manual fine-tuning configuration.
        """
        self.llm = llm or QwenClient()
        self.embedder = embedder or EmbeddingService()
        self.local_corpus = local_corpus or LocalCorpusClient()
        self.brave = brave
        self.perplexity = perplexity
        self.consensus = consensus
        self.compressed_index = compressed_index or CompressedVectorSidecar()
        self.hook_chain = hook_chain or HookChain()
        self.tuning_config = tuning_config or TuningConfig()

    def _build_context(
        self,
        brain_text: str,
        soul_text: str,
        chunks: list[dict[str, Any]],
        existing_nodes: list[dict[str, Any]],
    ) -> str:
        """Build a context string for the LLM from sources and existing graph."""
        context_parts = [
            "# Brain (approved knowledge)",
            brain_text,
            "# Soul (tone and policy)",
            soul_text,
            "# Source chunks",
        ]
        for chunk in chunks:
            context_parts.append(f"- {chunk['source_id']} [{chunk['start_index']}:{chunk['end_index']}]: {chunk['text']}")
        if existing_nodes:
            context_parts.append("# Existing nodes")
            for node in existing_nodes:
                context_parts.append(f"- {node['id']} ({node['node_type']}): {node['label']}")
        return "\n\n".join(context_parts)

    def extract_candidates(
        self,
        query: str,
        brain_text: str,
        soul_text: str,
        chunks: list[dict[str, Any]],
        existing_nodes: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Run the low-top-p extraction pass and return validated candidates.

        Args:
            query: The research question or topic.
            brain_text: Contents of brain.md.
            soul_text: Contents of soul.md.
            chunks: Retrieved source chunks.
            existing_nodes: Current graph nodes for context.

        Returns:
            A dictionary with validated nodes and edges.
        """
        existing_nodes = existing_nodes or []
        context = self._build_context(brain_text, soul_text, chunks, existing_nodes)
        user_prompt = f"Question/topic: {query}\n\n{context}\n\nExtract a JSON graph."
        try:
            result = self.llm.generate_json(
                EXTRACTION_SYSTEM_PROMPT, user_prompt, preset=EXTRACTION_PRESET
            )
        except ValueError as exc:
            logger.error("Extraction pass failed: %s", exc)
            return {"nodes": [], "edges": []}

        return self._validate_candidates(result)

    def generate_hypotheses(
        self,
        query: str,
        brain_text: str,
        soul_text: str,
        chunks: list[dict[str, Any]],
        existing_nodes: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Run the high-top-p hypothesis pass.

        Args:
            query: The research question or topic.
            brain_text: Contents of brain.md.
            soul_text: Contents of soul.md.
            chunks: Retrieved source chunks.
            existing_nodes: Current graph nodes for context.

        Returns:
            A dictionary with alternate queries and unverified hypotheses.
        """
        existing_nodes = existing_nodes or []
        context = self._build_context(brain_text, soul_text, chunks, existing_nodes)
        user_prompt = f"Question/topic: {query}\n\n{context}\n\nGenerate hypotheses and queries."
        try:
            result = self.llm.generate_json(
                HYPOTHESIS_SYSTEM_PROMPT, user_prompt, preset=HYPOTHESIS_PRESET
            )
        except ValueError as exc:
            logger.error("Hypothesis pass failed: %s", exc)
            return {"queries": [], "hypotheses": []}

        return result

    def _validate_candidates(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Validate extracted nodes and edges against serializers."""
        validated_nodes: list[dict[str, Any]] = []
        validated_edges: list[dict[str, Any]] = []

        for node in raw.get("nodes", []):
            try:
                validated = GraphNodeSerializer(**node)
                validated_nodes.append(validated.model_dump())
            except Exception as exc:
                logger.warning("Invalid node candidate: %s (%s)", node, exc)

        for edge in raw.get("edges", []):
            try:
                validated = GraphEdgeSerializer(**edge)
                validated_edges.append(validated.model_dump())
            except Exception as exc:
                logger.warning("Invalid edge candidate: %s (%s)", edge, exc)

        return {"nodes": validated_nodes, "edges": validated_edges}

    def evidence_gate(
        self,
        candidates: dict[str, Any],
        chunks: list[dict[str, Any]],
        external_sources: list[dict[str, Any]] | None = None,
        min_confidence: float = 0.6,
    ) -> dict[str, Any]:
        """Filter candidates by evidence-weighted consensus.

        A candidate passes only if it has at least one independent source
        (chunk or external source) and confidence >= min_confidence.

        Args:
            candidates: Validated nodes and edges.
            chunks: Source chunks used for retrieval.
            external_sources: Optional web/academic search results.
            min_confidence: Minimum confidence threshold.

        Returns:
            A dictionary with accepted and rejected candidates and audit trail.
        """
        external_sources = external_sources or []
        accepted: dict[str, Any] = {"nodes": [], "edges": []}
        rejected: dict[str, Any] = {"nodes": [], "edges": []}

        for node in candidates.get("nodes", []):
            provenance = self._build_provenance(node, chunks, external_sources)
            if node.get("confidence", 0.0) >= min_confidence and provenance:
                node["provenance"] = [p.model_dump() for p in provenance]
                accepted["nodes"].append(node)
            else:
                node["provenance"] = [p.model_dump() for p in provenance]
                rejected["nodes"].append(node)

        for edge in candidates.get("edges", []):
            provenance = self._build_provenance(edge, chunks, external_sources)
            if edge.get("confidence", 0.0) >= min_confidence and provenance:
                edge["provenance"] = [p.model_dump() for p in provenance]
                accepted["edges"].append(edge)
            else:
                edge["provenance"] = [p.model_dump() for p in provenance]
                rejected["edges"].append(edge)

        return {"accepted": accepted, "rejected": rejected, "audit": []}

    def _build_provenance(
        self,
        item: dict[str, Any],
        chunks: list[dict[str, Any]],
        external_sources: list[dict[str, Any]],
    ) -> list[ProvenanceSerializer]:
        """Build provenance records for an item from the best matching sources.

        Uses a simple keyword overlap heuristic to match sources to the item.
        """
        text = f"{item.get('label', '')} {item.get('description', '')} {item.get('edge_type', '')}"
        terms = set(text.lower().split())
        provenance: list[ProvenanceSerializer] = []

        for chunk in chunks[:5]:
            chunk_terms = set(chunk["text"].lower().split())
            overlap = len(terms & chunk_terms)
            if overlap >= 2:
                provenance.append(
                    ProvenanceSerializer(
                        source_id=chunk["source_id"],
                        source_span=f"{chunk['start_index']}:{chunk['end_index']}",
                        content_hash=chunk.get("content_hash", ""),
                        confidence=round(overlap / max(len(terms), 1), 2),
                        rationale="Keyword overlap with source chunk",
                    )
                )

        for source in external_sources[:3]:
            source_text = f"{source.get('title', '')} {source.get('snippet', '')}"
            source_terms = set(source_text.lower().split())
            overlap = len(terms & source_terms)
            if overlap >= 2:
                provenance.append(
                    ProvenanceSerializer(
                        source_id=source.get("url", source.get("id", "unknown")),
                        source_span="",
                        content_hash=hashlib.sha256(source_text.encode()).hexdigest()[:16],
                        confidence=round(overlap / max(len(terms), 1), 2),
                        rationale="External source overlap",
                    )
                )

        return provenance

    def research(
        self,
        query: str,
        brain_text: str = "",
        soul_text: str = "",
        existing_nodes: list[dict[str, Any]] | None = None,
        *,
        privacy_score: float = 0.5,
        routing_logits: list[float] | None = None,
    ) -> dict[str, Any]:
        """Run a full KAG research cycle with architecture-skill hooks.

        Args:
            query: Research question.
            brain_text: Contents of brain.md.
            soul_text: Contents of soul.md.
            existing_nodes: Current graph nodes.
            privacy_score: Privacy score (0-1) for the policy hook.
            routing_logits: Optional routing logits for the cascade hook.

        Returns:
            A dictionary with accepted candidates, rejected candidates,
            alternate queries, hypotheses, and hook-chain audit metadata.
        """
        import uuid

        existing_nodes = existing_nodes or []

        external_sources: list[dict[str, Any]] = []
        # Local corpus is the default evidence source (no API keys required).
        if self.local_corpus:
            external_sources.extend(self.local_corpus.search(query))
        # Optional remote providers only run when their API keys are configured.
        if self.brave:
            external_sources.extend(self.brave.search(query))
        if self.perplexity:
            external_sources.extend(self.perplexity.search(query))
        if self.consensus:
            external_sources.extend(self.consensus.search(query))

        # Canonical chunks + compressed sidecar indexing.
        chunks: list[dict[str, Any]] = [
            {
                "chunk_id": "chunk-brain",
                "source_id": "brain.md",
                "text": brain_text,
                "start_index": 0,
                "end_index": len(brain_text.split()),
                "content_hash": hashlib.sha256(brain_text.encode()).hexdigest()[:16],
                "sensitivity_tag": "internal",
                "route_hint": "LOCAL",
            },
            {
                "chunk_id": "chunk-soul",
                "source_id": "soul.md",
                "text": soul_text,
                "start_index": 0,
                "end_index": len(soul_text.split()),
                "content_hash": hashlib.sha256(soul_text.encode()).hexdigest()[:16],
                "sensitivity_tag": "internal",
                "route_hint": "LOCAL",
            },
        ]
        for source in external_sources:
            chunks.append(
                {
                    "chunk_id": f"chunk-{hashlib.sha256(source.get('url', source.get('id', '')).encode()).hexdigest()[:12]}",
                    "source_id": source.get("source", "web"),
                    "text": f"{source.get('title', '')} {source.get('snippet', '')}",
                    "start_index": 0,
                    "end_index": 0,
                    "content_hash": hashlib.sha256(
                        f"{source.get('title', '')}{source.get('snippet', '')}".encode()
                    ).hexdigest()[:16],
                    "sensitivity_tag": "public",
                    "route_hint": "CLOUD",
                }
            )

        # Asymmetric compressed retrieval (no full decompression in the loop).
        retrieved_chunks: list[dict[str, Any]] = []
        try:
            query_embedding = self.embedder.embed([query], is_query=True).tolist()[0]
            chunk_texts = [chunk["text"] for chunk in chunks]
            chunk_embeddings = self.embedder.embed(chunk_texts, is_query=False).tolist()
            for chunk, vector in zip(chunks, chunk_embeddings):
                self.compressed_index.add(
                    chunk_id=chunk["chunk_id"],
                    vector=vector,
                    source_id=chunk["source_id"],
                    text=chunk["text"],
                    sensitivity_tag=chunk.get("sensitivity_tag", "public"),
                    route_hint=chunk.get("route_hint", "LOCAL"),
                )
            retrieved_chunks = self.compressed_index.search(query_embedding, top_k=10)
        except RuntimeError as exc:
            logger.warning("Compressed retrieval skipped: %s", exc)
            retrieved_chunks = chunks[:10]

        candidates = self.extract_candidates(
            query, brain_text, soul_text, chunks, existing_nodes
        )
        gate_result = self.evidence_gate(candidates, chunks, external_sources)
        hypotheses = self.generate_hypotheses(
            query, brain_text, soul_text, chunks, existing_nodes
        )

        # Architecture-skill hook chain: conflict → cascade → policy.
        event = HookEvent(
            decision_id=str(uuid.uuid4()),
            query=query,
            context={
                "retrieved_chunks": retrieved_chunks,
                "permission_signal": [0.0, 1.0, 0.0, 1.0, 0.0],  # demo signal for conflict detection
                "node_a": "internal-policy",
                "node_b": "external-source",
            },
            routing_logits=routing_logits,
            privacy_score=privacy_score,
        )
        event = self.hook_chain.run(event)

        return {
            "accepted": gate_result["accepted"],
            "rejected": gate_result["rejected"],
            "queries": hypotheses.get("queries", []),
            "hypotheses": hypotheses.get("hypotheses", []),
            "external_sources": external_sources,
            "retrieved_chunks": retrieved_chunks,
            "hook_audit": event.audit_log,
            "routing": {
                "selected_target": event.selected_target,
                "probability_vector": event.probability_vector,
                "blocked": event.blocked,
                "block_reason": event.block_reason,
            },
            "filtered_context": event.filtered_context,
            "tuning_config": self.tuning_config.to_dict(),
        }
