from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence


@dataclass
class DocumentMetadata:
    source: str
    page: int | None = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "page": self.page,
            "extra": self.extra,
        }


@dataclass
class ChunkInput:
    id: str
    text: str
    metadata: DocumentMetadata


@dataclass
class DocumentChunk:
    id: str
    text: str
    metadata: DocumentMetadata
    embedding: List[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata.to_dict(),
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DocumentChunk":
        metadata = payload.get("metadata", {})
        return cls(
            id=payload["id"],
            text=payload["text"],
            metadata=DocumentMetadata(
                source=metadata.get("source", "unknown"),
                page=metadata.get("page"),
                extra=metadata.get("extra", {}),
            ),
            embedding=list(payload["embedding"]),
        )


@dataclass
class IngestedDocument:
    path: Path
    chunks: Sequence[DocumentChunk]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "chunks": [chunk.to_dict() for chunk in self.chunks],
        }
