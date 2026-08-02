"""Pydantic serializers for graph payloads and validation."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProvenanceSerializer(BaseModel):
    """Provenance record for a graph node or edge."""

    source_id: str
    source_span: str = ""
    content_hash: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    rationale: str = ""


class GraphNodeSerializer(BaseModel):
    """Validated graph node payload."""

    id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    label: str = Field(min_length=1, max_length=512)
    node_type: str = Field(min_length=1, max_length=128)
    description: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: list[ProvenanceSerializer] = Field(default_factory=list)

    @field_validator("id", "node_type")
    @classmethod
    def lower_and_strip(cls, value: str) -> str:
        return value.strip().lower()


class GraphEdgeSerializer(BaseModel):
    """Validated graph edge payload."""

    id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    source_id: str
    target_id: str
    edge_type: str = Field(min_length=1, max_length=128)
    label: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: list[ProvenanceSerializer] = Field(default_factory=list)

    @field_validator("edge_type")
    @classmethod
    def lower_and_strip(cls, value: str) -> str:
        return value.strip().lower()


class ChunkSerializer(BaseModel):
    """Validated chunk payload."""

    source_id: str
    source_type: str = "document"
    text: str = Field(min_length=1)
    start_index: int = Field(ge=0, default=0)
    end_index: int = Field(ge=0, default=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BatchImportSerializer(BaseModel):
    """Validated batch import payload."""

    nodes: list[GraphNodeSerializer] = Field(default_factory=list)
    edges: list[GraphEdgeSerializer] = Field(default_factory=list)
    dry_run: bool = True
    replace_existing: bool = False
