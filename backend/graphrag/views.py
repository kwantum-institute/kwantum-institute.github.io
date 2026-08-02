"""REST API views for the KAG GraphRAG editor."""

import json
import logging
from pathlib import Path
from typing import Any

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Chunk, GraphEdge, GraphNode, ProvenanceEntry
from .serializers import (
    BatchImportSerializer,
    GraphEdgeSerializer,
    GraphNodeSerializer,
    ProvenanceSerializer,
)
from .services.batch_processor import BatchProcessor
from .services.embedding import EmbeddingService
from .services.external_search import (
    BraveSearchClient,
    ConsensusClient,
    LocalCorpusClient,
    OperaClient,
    PerplexityClient,
)
from .services.kag_engine import KAGEngine
from .services.llm import QwenClient
from .services.mermaid_generator import MermaidGenerator
from .services.tuning import ManualTuner, TuningConfig

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BRAIN_PATH = REPO_ROOT / "brain.md"
SOUL_PATH = REPO_ROOT / "soul.md"


def _load_text(path: Path) -> str:
    """Load text from a file, returning an empty string if missing."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _json_error(message: str, status: int = 400) -> JsonResponse:
    """Return a JSON error response."""
    return JsonResponse({"error": message}, status=status)


class NodeListView(View):
    """List all graph nodes or create a new one."""

    def get(self, _request: Any) -> JsonResponse:
        nodes = list(GraphNode.objects.values())
        return JsonResponse({"nodes": nodes})

    @method_decorator(csrf_exempt)
    def post(self, request: Any) -> JsonResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json_error("Invalid JSON")

        try:
            serializer = GraphNodeSerializer(**data)
        except Exception as exc:
            return _json_error(f"Validation error: {exc}")

        node, _ = GraphNode.objects.update_or_create(
            id=serializer.id,
            defaults={
                "label": serializer.label,
                "node_type": serializer.node_type,
                "description": serializer.description,
                "confidence": serializer.confidence,
                "metadata": serializer.metadata,
            },
        )
        return JsonResponse({"node": {"id": node.id, "label": node.label}})


class NodeDetailView(View):
    """Retrieve, update, or delete a single graph node."""

    def get(self, _request: Any, pk: str) -> JsonResponse:
        try:
            node = GraphNode.objects.values().get(pk=pk)
        except GraphNode.DoesNotExist:
            return _json_error("Node not found", 404)
        return JsonResponse({"node": node})

    @method_decorator(csrf_exempt)
    def patch(self, request: Any, pk: str) -> JsonResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json_error("Invalid JSON")

        try:
            serializer = GraphNodeSerializer(**data)
        except Exception as exc:
            return _json_error(f"Validation error: {exc}")

        GraphNode.objects.filter(pk=pk).update(
            label=serializer.label,
            node_type=serializer.node_type,
            description=serializer.description,
            confidence=serializer.confidence,
            metadata=serializer.metadata,
        )
        return JsonResponse({"updated": pk})

    @method_decorator(csrf_exempt)
    def delete(self, _request: Any, pk: str) -> JsonResponse:
        GraphNode.objects.filter(pk=pk).delete()
        return JsonResponse({"deleted": pk})


class EdgeListView(View):
    """List all graph edges or create a new one."""

    def get(self, _request: Any) -> JsonResponse:
        edges = list(
            GraphEdge.objects.values(
                "id", "source_id", "target_id", "edge_type", "label", "confidence"
            )
        )
        return JsonResponse({"edges": edges})

    @method_decorator(csrf_exempt)
    def post(self, request: Any) -> JsonResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json_error("Invalid JSON")

        try:
            serializer = GraphEdgeSerializer(**data)
        except Exception as exc:
            return _json_error(f"Validation error: {exc}")

        try:
            source = GraphNode.objects.get(pk=serializer.source_id)
            target = GraphNode.objects.get(pk=serializer.target_id)
        except GraphNode.DoesNotExist:
            return _json_error("Source or target node not found", 404)

        edge, _ = GraphEdge.objects.update_or_create(
            id=serializer.id,
            defaults={
                "source": source,
                "target": target,
                "edge_type": serializer.edge_type,
                "label": serializer.label,
                "confidence": serializer.confidence,
                "metadata": serializer.metadata,
            },
        )
        return JsonResponse({"edge": {"id": edge.id, "type": edge.edge_type}})


class EdgeDetailView(View):
    """Retrieve, update, or delete a single graph edge."""

    def get(self, _request: Any, pk: str) -> JsonResponse:
        try:
            edge = GraphEdge.objects.values().get(pk=pk)
        except GraphEdge.DoesNotExist:
            return _json_error("Edge not found", 404)
        return JsonResponse({"edge": edge})

    @method_decorator(csrf_exempt)
    def delete(self, _request: Any, pk: str) -> JsonResponse:
        GraphEdge.objects.filter(pk=pk).delete()
        return JsonResponse({"deleted": pk})


class SemanticSearchView(View):
    """Run semantic search over embedded chunks and return relevant chunks."""

    def get(self, request: Any) -> JsonResponse:
        import numpy as np

        query = request.GET.get("q", "").strip()
        if not query:
            return _json_error("Missing query parameter 'q'")

        embedder = EmbeddingService()
        try:
            query_embedding = embedder.embed([query], is_query=True)
        except RuntimeError as exc:
            return _json_error(str(exc), 503)

        query_norm = np.linalg.norm(query_embedding[0])
        chunks = list(Chunk.objects.values("id", "source_id", "text", "embedding"))
        results = []
        for chunk in chunks:
            embedding = chunk.get("embedding")
            if embedding:
                chunk_vec = np.asarray(embedding, dtype=np.float32)
            else:
                chunk_vec = embedder.embed([chunk["text"]], is_query=False)[0]
            chunk_norm = np.linalg.norm(chunk_vec)
            if chunk_norm == 0:
                continue
            similarity = float(np.dot(query_embedding[0], chunk_vec) / (query_norm * chunk_norm))
            results.append(
                {
                    "id": chunk["id"],
                    "source_id": chunk["source_id"],
                    "text": chunk["text"][:300],
                    "score": round(similarity, 4),
                }
            )
        results.sort(key=lambda r: r["score"], reverse=True)
        return JsonResponse({"results": results[:20]})


class BatchImportView(View):
    """Import nodes and edges from CSV/JSON with dry-run support."""

    @method_decorator(csrf_exempt)
    def post(self, request: Any) -> JsonResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json_error("Invalid JSON")

        processor = BatchProcessor()

        # Accept either a CSV string or a JSON payload.
        csv_text = data.get("csv")
        if csv_text:
            payload = processor.import_csv(csv_text)
        else:
            payload = data

        dry_run = payload.get("dry_run", True)
        replace_existing = payload.get("replace_existing", False)

        try:
            BatchImportSerializer(**payload)
        except Exception as exc:
            return _json_error(f"Validation error: {exc}")

        if dry_run:
            return JsonResponse(processor.dry_run(payload))

        result = processor.apply_batch(payload, replace_existing=replace_existing)
        return JsonResponse(result)


class MermaidExportView(View):
    """Export the current graph as Mermaid syntax and Markdown."""

    def get(self, request: Any) -> JsonResponse:
        nodes = list(GraphNode.objects.values())
        edges = list(
            GraphEdge.objects.values(
                "id", "source_id", "target_id", "edge_type", "label", "confidence"
            )
        )
        generator = MermaidGenerator()
        mermaid = generator.to_mermaid(nodes, edges)
        markdown = generator.to_markdown(nodes, edges, title="Kwantum Institute Graph")
        return JsonResponse({"mermaid": mermaid, "markdown": markdown})


class ProvenanceListView(View):
    """List provenance entries for a target node or edge."""

    def get(self, request: Any) -> JsonResponse:
        target_id = request.GET.get("target_id")
        target_type = request.GET.get("target_type")
        queryset = ProvenanceEntry.objects.all()
        if target_id:
            queryset = queryset.filter(target_id=target_id)
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        entries = list(queryset.values())
        return JsonResponse({"provenance": entries})

    @method_decorator(csrf_exempt)
    def post(self, request: Any) -> JsonResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json_error("Invalid JSON")

        try:
            serializer = ProvenanceSerializer(**data)
        except Exception as exc:
            return _json_error(f"Validation error: {exc}")

        entry = ProvenanceEntry.objects.create(
            target_id=data.get("target_id", ""),
            target_type=data.get("target_type", "node"),
            source_id=serializer.source_id,
            source_span=serializer.source_span,
            content_hash=serializer.content_hash,
            confidence=serializer.confidence,
            rationale=serializer.rationale,
        )
        return JsonResponse({"provenance": {"id": entry.id, "target_id": entry.target_id}})


class ResearchView(View):
    """Run a KAG research cycle and return accepted candidates."""

    @method_decorator(csrf_exempt)
    def post(self, request: Any) -> JsonResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json_error("Invalid JSON")

        query = data.get("query", "").strip()
        if not query:
            return _json_error("Missing 'query' field")

        privacy_score = float(data.get("privacy_score", 0.5))
        routing_logits = data.get("routing_logits")

        brain_text = _load_text(BRAIN_PATH)
        soul_text = _load_text(SOUL_PATH)
        existing_nodes = list(GraphNode.objects.values("id", "label", "node_type", "description"))

        engine = KAGEngine(
            llm=QwenClient(),
            embedder=EmbeddingService(),
            local_corpus=LocalCorpusClient(),
            # Optional remote providers: only active when API keys exist.
            brave=BraveSearchClient(),
            perplexity=PerplexityClient(),
            consensus=ConsensusClient(),
        )
        try:
            result = engine.research(
                query,
                brain_text,
                soul_text,
                existing_nodes,
                privacy_score=privacy_score,
                routing_logits=routing_logits,
            )
        except RuntimeError as exc:
            return _json_error(str(exc), 503)

        return JsonResponse(result)


class ArchitectureView(View):
    """Return the architecture-skill Mermaid diagram and explanation."""

    def get(self, _request: Any) -> JsonResponse:
        generator = MermaidGenerator()
        mermaid = generator.to_architecture_mermaid(title="KAG GraphRAG Architecture")
        return JsonResponse(
            {
                "mermaid": mermaid,
                "principles": [
                    "Asymmetric compressed retrieval: canonical store + compressed sidecar",
                    "Hook chain: conflict detection → cascade routing → policy filter",
                    "Manual fine-tuning: config-first, epoch checkpoints, keep/revert",
                    "Append-only audit logging for every routing decision",
                ],
            }
        )


class TuneView(View):
    """Run a manual fine-tuning baseline or training pass."""

    @method_decorator(csrf_exempt)
    def post(self, request: Any) -> JsonResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json_error("Invalid JSON")

        config = TuningConfig(**data.get("config", {}))
        baseline_only = data.get("baseline_only", False)
        X = data.get("X", [[0.5, 0.5, 0.5], [0.9, 0.1, 0.9], [0.1, 0.9, 0.1]])
        y = data.get("y", [0, 2, 1])

        tuner = ManualTuner(config)
        try:
            result = tuner.train(X, y, baseline_only=baseline_only)
        except Exception as exc:
            return _json_error(f"Training failed: {exc}")

        return JsonResponse(result)
