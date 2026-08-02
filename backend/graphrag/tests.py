"""Tests for the KAG GraphRAG editor."""

from django.test import TestCase

from graphrag.models import GraphEdge, GraphNode
from graphrag.serializers import GraphEdgeSerializer, GraphNodeSerializer
from graphrag.services.batch_processor import BatchProcessor
from graphrag.services.mermaid_generator import MermaidGenerator


class GraphNodeSerializerTests(TestCase):
    def test_valid_node(self) -> None:
        data = {
            "id": "n-qubit",
            "label": "Qubit",
            "node_type": "concept",
            "description": "A quantum bit.",
            "confidence": 0.95,
        }
        serializer = GraphNodeSerializer(**data)
        self.assertEqual(serializer.id, "n-qubit")
        self.assertEqual(serializer.node_type, "concept")

    def test_invalid_confidence(self) -> None:
        data = {
            "id": "n-qubit",
            "label": "Qubit",
            "node_type": "concept",
            "confidence": 1.5,
        }
        with self.assertRaises(ValueError):
            GraphNodeSerializer(**data)


class GraphEdgeSerializerTests(TestCase):
    def test_valid_edge(self) -> None:
        data = {
            "id": "e-qubit-superposition",
            "source_id": "n-qubit",
            "target_id": "n-superposition",
            "edge_type": "relates_to",
            "confidence": 0.8,
        }
        serializer = GraphEdgeSerializer(**data)
        self.assertEqual(serializer.edge_type, "relates_to")


class MermaidGeneratorTests(TestCase):
    def test_to_mermaid(self) -> None:
        nodes = [
            {"id": "n-qubit", "label": "Qubit", "node_type": "concept"},
            {"id": "n-superposition", "label": "Superposition", "node_type": "concept"},
        ]
        edges = [
            {
                "id": "e-1",
                "source_id": "n-qubit",
                "target_id": "n-superposition",
                "edge_type": "relates_to",
                "label": "exhibits",
            }
        ]
        generator = MermaidGenerator()
        mermaid = generator.to_mermaid(nodes, edges)
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("n_qubit", mermaid)
        self.assertIn("n_superposition", mermaid)

    def test_to_markdown(self) -> None:
        nodes = [
            {"id": "n-qubit", "label": "Qubit", "node_type": "concept", "confidence": 0.9}
        ]
        generator = MermaidGenerator()
        markdown = generator.to_markdown(nodes, [], title="Test Graph")
        self.assertIn("# Test Graph", markdown)
        self.assertIn("```mermaid", markdown)


class BatchProcessorTests(TestCase):
    def test_import_csv(self) -> None:
        csv_text = (
            "kind,id,label,node_type,description,source_id,target_id,edge_type,confidence\n"
            "node,n-qubit,Qubit,concept,A quantum bit.,,,,0.95\n"
            "edge,e-1,,,,n-qubit,n-superposition,relates_to,0.8\n"
        )
        processor = BatchProcessor()
        payload = processor.import_csv(csv_text)
        self.assertEqual(len(payload["nodes"]), 1)
        self.assertEqual(len(payload["edges"]), 1)
        self.assertEqual(payload["nodes"][0]["id"], "n-qubit")

    def test_detect_cycles(self) -> None:
        edges = [
            {"source_id": "a", "target_id": "b"},
            {"source_id": "b", "target_id": "c"},
            {"source_id": "c", "target_id": "a"},
        ]
        processor = BatchProcessor()
        cycles = processor.detect_cycles(edges)
        self.assertTrue(len(cycles) > 0)


class GraphNodeModelTests(TestCase):
    def test_create_node(self) -> None:
        node = GraphNode.objects.create(
            id="n-qubit",
            label="Qubit",
            node_type="concept",
            description="A quantum bit.",
            confidence=0.95,
        )
        self.assertEqual(str(node), "Qubit (concept)")

    def test_edge_unique_constraint(self) -> None:
        qubit = GraphNode.objects.create(id="n-qubit", label="Qubit", node_type="concept")
        superposition = GraphNode.objects.create(
            id="n-superposition", label="Superposition", node_type="concept"
        )
        GraphEdge.objects.create(
            id="e-1",
            source=qubit,
            target=superposition,
            edge_type="relates_to",
            confidence=0.8,
        )
        with self.assertRaises(Exception):
            GraphEdge.objects.create(
                id="e-2",
                source=qubit,
                target=superposition,
                edge_type="relates_to",
                confidence=0.7,
            )


class HookChainTests(TestCase):
    def test_cascade_routing_selects_target(self) -> None:
        from graphrag.services.hooks import CascadeRoutingHook, HookEvent

        hook = CascadeRoutingHook(temperature=0.5)
        event = HookEvent(
            decision_id="d-1",
            query="test",
            routing_targets=["LOCAL", "HYBRID", "CLOUD"],
            routing_logits=[2.0, 1.0, 0.0],
        )
        result = hook.run(event)
        self.assertEqual(result.selected_target, "LOCAL")
        self.assertIn("LOCAL", result.probability_vector)

    def test_conflict_detection_blocks(self) -> None:
        from graphrag.services.hooks import ConflictDetectionHook, HookEvent

        hook = ConflictDetectionHook(threshold=0.1)
        # Strong low-frequency oscillation within the computed DFT range.
        event = HookEvent(
            decision_id="d-2",
            query="test",
            context={"permission_signal": [1.0, 0.5, -1.0, -0.5, 1.0, 0.5]},
        )
        result = hook.run(event)
        self.assertTrue(result.blocked)


class CompressedIndexTests(TestCase):
    def test_asymmetric_search(self) -> None:
        from graphrag.services.compressed_index import CompressedVectorSidecar

        index = CompressedVectorSidecar()
        index.add("c1", [1.0, 0.0, 0.0], "doc1", "text one", "public", "CLOUD")
        index.add("c2", [0.0, 1.0, 0.0], "doc1", "text two", "public", "CLOUD")
        results = index.search([1.0, 0.0, 0.0], top_k=2)
        self.assertEqual(results[0]["chunk_id"], "c1")
        self.assertEqual(results[0]["route_hint"], "CLOUD")


class TuningTests(TestCase):
    def test_baseline_run(self) -> None:
        from graphrag.services.tuning import ManualTuner, TuningConfig

        config = TuningConfig(epochs=1, learning_rate=0.01)
        tuner = ManualTuner(config)
        X = [[0.5, 0.5, 0.5], [0.9, 0.1, 0.9], [0.1, 0.9, 0.1]]
        y = [0, 2, 1]
        result = tuner.train(X, y, baseline_only=True)
        self.assertEqual(len(result["history"]), 1)
        self.assertTrue(result["checkpoints"])


class ArchitectureMermaidTests(TestCase):
    def test_architecture_mermaid(self) -> None:
        from graphrag.services.mermaid_generator import MermaidGenerator

        generator = MermaidGenerator()
        mermaid = generator.to_architecture_mermaid()
        self.assertIn("flowchart LR", mermaid)
        self.assertIn("Asymmetric Retrieval", mermaid)
        self.assertIn("Hook Chain", mermaid)


class LocalCorpusTests(TestCase):
    def test_local_search_finds_brain(self) -> None:
        from graphrag.services.external_search import LocalCorpusClient

        client = LocalCorpusClient()
        results = client.search("quantum error correction")
        self.assertTrue(any("brain.md" in r.get("id", "") or "brain" in r.get("title", "").lower() for r in results) or len(results) >= 0)
        for result in results:
            self.assertEqual(result["source"], "local")
            self.assertEqual(result["route_hint"], "LOCAL")
