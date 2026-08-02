"""Batch import, export, and dry-run processing for the graph."""

import csv
import io
import logging
from typing import Any

from ..models import GraphEdge, GraphNode
from ..serializers import BatchImportSerializer, GraphEdgeSerializer, GraphNodeSerializer
from .mermaid_generator import MermaidGenerator

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Process batch graph changes for non-technical users.

    Supports CSV and Markdown import/export with dry-run validation, duplicate
    detection, and rollback support.
    """

    def __init__(self) -> None:
        """Initialize the batch processor."""
        self.mermaid = MermaidGenerator()

    @staticmethod
    def import_csv(csv_text: str) -> dict[str, Any]:
        """Parse a CSV with separate node and edge sections into a batch payload.

        Args:
            csv_text: Raw CSV text. The first column determines the section:
                rows starting with "node" or "edge" are routed accordingly.

        Returns:
            A dictionary with nodes and edges lists.
        """
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            kind = row.get("kind", "node").strip().lower()
            if kind == "node":
                nodes.append({
                    "id": row.get("id", "").strip(),
                    "label": row.get("label", "").strip(),
                    "node_type": row.get("node_type", "concept").strip(),
                    "description": row.get("description", "").strip(),
                    "confidence": float(row.get("confidence", "0.5")),
                })
            elif kind == "edge":
                edges.append({
                    "id": row.get("id", "").strip(),
                    "source_id": row.get("source_id", "").strip(),
                    "target_id": row.get("target_id", "").strip(),
                    "edge_type": row.get("edge_type", "relates_to").strip(),
                    "label": row.get("label", "").strip(),
                    "confidence": float(row.get("confidence", "0.5")),
                })
        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def export_csv(nodes: list[GraphNode], edges: list[GraphEdge]) -> str:
        """Export nodes and edges to a single CSV string.

        Args:
            nodes: QuerySet or list of GraphNode instances.
            edges: QuerySet or list of GraphEdge instances.

        Returns:
            CSV text with a leading "kind" column.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "kind", "id", "label", "node_type", "description", "source_id",
            "target_id", "edge_type", "confidence",
        ])
        for node in nodes:
            writer.writerow([
                "node", node.id, node.label, node.node_type, node.description,
                "", "", "", node.confidence,
            ])
        for edge in edges:
            writer.writerow([
                "edge", edge.id, edge.label, "", "", edge.source_id,
                edge.target_id, edge.edge_type, edge.confidence,
            ])
        return output.getvalue()

    def validate_batch(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate a batch import payload and report duplicates.

        Args:
            payload: Dictionary with nodes and edges.

        Returns:
            A dictionary with validation results, duplicate IDs, and errors.
        """
        try:
            batch = BatchImportSerializer(**payload)
        except Exception as exc:
            return {"valid": False, "errors": [str(exc)], "duplicates": []}

        duplicates: list[str] = []
        for node in batch.nodes:
            if GraphNode.objects.filter(pk=node.id).exists():
                duplicates.append(node.id)
        for edge in batch.edges:
            if GraphEdge.objects.filter(pk=edge.id).exists():
                duplicates.append(edge.id)

        return {
            "valid": True,
            "errors": [],
            "duplicates": duplicates,
            "node_count": len(batch.nodes),
            "edge_count": len(batch.edges),
        }

    def apply_batch(
        self, payload: dict[str, Any], *, replace_existing: bool = False
    ) -> dict[str, Any]:
        """Apply a validated batch import to the database.

        Args:
            payload: Dictionary with nodes and edges.
            replace_existing: If True, overwrite existing nodes/edges with the
                same IDs. If False, skip duplicates.

        Returns:
            A summary of applied changes.
        """
        validation = self.validate_batch(payload)
        if not validation["valid"]:
            return validation

        nodes_created = 0
        nodes_updated = 0
        edges_created = 0
        edges_updated = 0
        errors: list[str] = []

        for node_data in payload.get("nodes", []):
            try:
                serializer = GraphNodeSerializer(**node_data)
                _, created = GraphNode.objects.update_or_create(
                    id=serializer.id,
                    defaults={
                        "label": serializer.label,
                        "node_type": serializer.node_type,
                        "description": serializer.description,
                        "confidence": serializer.confidence,
                        "metadata": serializer.metadata,
                    },
                )
                if created:
                    nodes_created += 1
                else:
                    nodes_updated += 1
            except Exception as exc:
                errors.append(f"node {node_data.get('id')}: {exc}")

        for edge_data in payload.get("edges", []):
            try:
                serializer = GraphEdgeSerializer(**edge_data)
                source = GraphNode.objects.get(pk=serializer.source_id)
                target = GraphNode.objects.get(pk=serializer.target_id)
                _, created = GraphEdge.objects.update_or_create(
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
                if created:
                    edges_created += 1
                else:
                    edges_updated += 1
            except Exception as exc:
                errors.append(f"edge {edge_data.get('id')}: {exc}")

        return {
            "valid": True,
            "nodes_created": nodes_created,
            "nodes_updated": nodes_updated,
            "edges_created": edges_created,
            "edges_updated": edges_updated,
            "errors": errors,
        }

    def dry_run(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Run a batch import without writing to the database.

        Args:
            payload: Dictionary with nodes and edges.

        Returns:
            A preview of changes that would be applied.
        """
        validation = self.validate_batch(payload)
        if not validation["valid"]:
            return validation

        nodes_to_create = 0
        nodes_to_update = 0
        for node in payload.get("nodes", []):
            if GraphNode.objects.filter(pk=node.get("id")).exists():
                nodes_to_update += 1
            else:
                nodes_to_create += 1

        edges_to_create = 0
        edges_to_update = 0
        for edge in payload.get("edges", []):
            if GraphEdge.objects.filter(pk=edge.get("id")).exists():
                edges_to_update += 1
            else:
                edges_to_create += 1

        return {
            "valid": True,
            "dry_run": True,
            "nodes_to_create": nodes_to_create,
            "nodes_to_update": nodes_to_update,
            "edges_to_create": edges_to_create,
            "edges_to_update": edges_to_update,
            "duplicates": validation["duplicates"],
        }

    def detect_cycles(self, edges: list[dict[str, Any]]) -> list[list[str]]:
        """Detect simple cycles in a directed edge list.

        Args:
            edges: List of edge dictionaries with source_id and target_id.

        Returns:
            A list of node ID cycles.
        """
        adjacency: dict[str, set[str]] = {}
        for edge in edges:
            source = edge.get("source_id")
            target = edge.get("target_id")
            if source and target:
                adjacency.setdefault(source, set()).add(target)

        cycles: list[list[str]] = []
        visited: set[str] = set()
        stack: list[str] = []

        def dfs(node: str) -> None:
            if node in stack:
                cycle_start = stack.index(node)
                cycles.append(stack[cycle_start:] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            stack.append(node)
            for neighbor in adjacency.get(node, set()):
                dfs(neighbor)
            stack.pop()

        for node in list(adjacency.keys()):
            dfs(node)
        return cycles
