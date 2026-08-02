from django.db import models


class GraphNode(models.Model):
    """A typed entity in the knowledge graph."""

    id = models.CharField(max_length=128, primary_key=True)
    label = models.CharField(max_length=512)
    node_type = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    confidence = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["label"]

    def __str__(self) -> str:
        return f"{self.label} ({self.node_type})"


class GraphEdge(models.Model):
    """A typed relationship between two graph nodes."""

    id = models.CharField(max_length=128, primary_key=True)
    source = models.ForeignKey(
        GraphNode, on_delete=models.CASCADE, related_name="outgoing_edges"
    )
    target = models.ForeignKey(
        GraphNode, on_delete=models.CASCADE, related_name="incoming_edges"
    )
    edge_type = models.CharField(max_length=128)
    label = models.CharField(max_length=512, blank=True)
    confidence = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["source__label", "edge_type", "target__label"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "target", "edge_type"],
                name="unique_edge_type_per_pair",
            )
        ]

    def __str__(self) -> str:
        return f"{self.source} --{self.edge_type}--> {self.target}"


class Chunk(models.Model):
    """A chunk of source text with its embedding vector."""

    id = models.CharField(max_length=128, primary_key=True)
    source_id = models.CharField(max_length=512)
    source_type = models.CharField(max_length=128)
    text = models.TextField()
    embedding = models.JSONField(default=list, blank=True)
    start_index = models.IntegerField(default=0)
    end_index = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["source_id", "start_index"]

    def __str__(self) -> str:
        return f"{self.source_id}:{self.start_index}-{self.end_index}"


class ProvenanceEntry(models.Model):
    """A provenance record for a graph node or edge."""

    id = models.CharField(max_length=128, primary_key=True)
    target_id = models.CharField(max_length=128)
    target_type = models.CharField(
        max_length=16, choices=[("node", "Node"), ("edge", "Edge")]
    )
    source_id = models.CharField(max_length=512)
    source_span = models.CharField(max_length=512, blank=True)
    content_hash = models.CharField(max_length=128, blank=True)
    confidence = models.FloatField(default=0.0)
    rationale = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Provenance for {self.target_type} {self.target_id}"
