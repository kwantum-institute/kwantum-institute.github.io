"""Generate Mermaid flowcharts and Markdown views from canonical graph state."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MermaidGenerator:
    """Render a graph as Mermaid syntax and a Markdown document."""

    def __init__(self) -> None:
        """Initialize the Mermaid generator."""
        pass

    @staticmethod
    def _safe_id(value: str) -> str:
        """Return a Mermaid-safe node ID from a graph ID."""
        return value.replace("-", "_").replace(" ", "_")

    @staticmethod
    def _quote_label(label: str) -> str:
        """Wrap a label in double quotes if it contains special characters."""
        if any(c in label for c in '()[]{},:;"'):
            escaped = label.replace('"', '\\"')
            return f'"{escaped}"'
        return label

    def to_mermaid(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> str:
        """Generate a Mermaid flowchart from nodes and edges.

        Args:
            nodes: Graph nodes with id, label, and node_type.
            edges: Graph edges with source_id, target_id, edge_type, and label.

        Returns:
            Mermaid flowchart syntax as a string.
        """
        lines = ["flowchart TD"]
        type_groups: dict[str, list[str]] = {}

        for node in nodes:
            node_id = self._safe_id(node["id"])
            label = self._quote_label(node.get("label", node["id"]))
            node_type = node.get("node_type", "node")
            line = f"    {node_id}[{label}]"
            lines.append(line)
            type_groups.setdefault(node_type, []).append(node_id)

        for edge in edges:
            source = self._safe_id(edge["source_id"])
            target = self._safe_id(edge["target_id"])
            edge_type = edge.get("edge_type", "relates_to")
            edge_label = edge.get("label") or edge_type
            edge_label = self._quote_label(edge_label)
            lines.append(f"    {source} -->|{edge_label}| {target}")

        # Group nodes by type in subgraphs for readability.
        for node_type, node_ids in type_groups.items():
            safe_type = self._safe_id(node_type)
            lines.append(f"    subgraph {safe_type} [{node_type}]")
            for node_id in node_ids:
                lines.append(f"        {node_id}")
            lines.append("    end")

        return "\n".join(lines)

    def to_markdown(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]], title: str = "Knowledge Graph"
    ) -> str:
        """Generate a Markdown document with a Mermaid diagram.

        Args:
            nodes: Graph nodes.
            edges: Graph edges.
            title: Document title.

        Returns:
            Markdown string with a human-readable summary and a Mermaid block.
        """
        lines = [f"# {title}", ""]

        if nodes:
            lines.append(f"## Nodes ({len(nodes)})")
            for node in nodes:
                confidence = node.get("confidence", 0.0)
                lines.append(
                    f"- **{node.get('label', node['id'])}** ({node.get('node_type', 'node')})"
                    f" — confidence: {confidence}"
                )
                if node.get("description"):
                    lines.append(f"  - {node['description']}")
            lines.append("")

        if edges:
            lines.append(f"## Relationships ({len(edges)})")
            for edge in edges:
                lines.append(
                    f"- {edge.get('source_id')} → {edge.get('target_id')}"
                    f" ({edge.get('edge_type', 'relates_to')})"
                )
            lines.append("")

        lines.append("## Diagram")
        lines.append("```mermaid")
        lines.append(self.to_mermaid(nodes, edges))
        lines.append("```")
        return "\n".join(lines)

    def to_architecture_mermaid(self, title: str = "Architecture Flow") -> str:
        """Generate a Mermaid diagram of the architecture-skill hook chain.

        Args:
            title: Diagram title.

        Returns:
            Mermaid flowchart syntax for the architecture flow.
        """
        lines = [
            "flowchart LR",
            "    subgraph inputs [Inputs]",
            "        brain[brain.md]",
            "        soul[soul.md]",
            "        web[Web Sources]",
            "    end",
            "    subgraph retrieval [Asymmetric Retrieval]",
            "        canonical[Canonical Store]",
            "        sidecar[Compressed Sidecar]",
            "        scorer[Asymmetric Scorer]",
            "    end",
            "    subgraph hooks [Hook Chain]",
            "        conflict[Conflict Detection]",
            "        cascade[Cascade Routing]",
            "        policy[Policy Filter]",
            "    end",
            "    subgraph output [Output]",
            "        audit[Audit Log]",
            "        generator[Generator]",
            "    end",
            "    brain --> canonical",
            "    soul --> canonical",
            "    web --> canonical",
            "    canonical --> sidecar",
            "    sidecar --> scorer",
            "    scorer --> conflict",
            "    conflict -->|allow| cascade",
            "    conflict -->|block| audit",
            "    cascade --> policy",
            "    policy --> generator",
            "    generator --> audit",
            f"    %% {title}",
        ]
        return "\n".join(lines)
