from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from supabase import Client

try:  # pragma: no cover - optional dependency detail
    from postgrest import APIError
except ImportError:  # pragma: no cover
    APIError = None  # type: ignore[misc, assignment]

from .types import DocumentChunk, DocumentMetadata


@dataclass
class RankedChunk:
    chunk: DocumentChunk
    score: Optional[float] = None


class SupabaseVectorStore:
    def __init__(self, client: Client, *, table: str, query_function: str) -> None:
        self._client = client
        self._table = table
        self._query_function = query_function

    def is_empty(self) -> bool:
        response = (
            self._client.table(self._table)
            .select("id", count="exact", head=True)
            .execute()
        )
        count = getattr(response, "count", None)
        if count is None:
            return False  # fall back to assuming data exists
        return count == 0

    def add_chunks(self, chunks: Iterable[DocumentChunk]) -> None:
        payload = [
            {
                "id": chunk.id,
                "doc_id": chunk.metadata.source,
                "chunk_index": int(chunk.metadata.extra.get("chunk_index", 0)),
                "content": chunk.text,
                "metadata": chunk.metadata.to_dict(),
                "embedding": chunk.embedding,
            }
            for chunk in chunks
        ]
        if not payload:
            return
        try:
            self._client.table(self._table).upsert(payload).execute()
        except Exception as exc:  # pragma: no cover - runtime feedback
            if APIError is not None and isinstance(exc, APIError):
                message = getattr(exc, "message", "")
                if "dimensions" in message.lower():
                    actual = len(payload[0]["embedding"])
                    raise RuntimeError(
                        "Supabase vector column dimension mismatch. "
                        f"Current embeddings have {actual} dimensions. "
                        "Update the table definition or switch to a matching embedding model."
                    ) from exc
            raise

    def top_k(self, query_embedding: List[float], k: int = 5) -> List[RankedChunk]:
        response = self._client.rpc(
            self._query_function,
            {
                "query_embedding": query_embedding,
                "match_count": k,
            },
        ).execute()

        data = getattr(response, "data", None) or []
        ranked: List[RankedChunk] = []
        for item in data:
            metadata_payload = item.get("metadata") or {}
            metadata = DocumentMetadata(
                source=metadata_payload.get("source", "unknown"),
                page=metadata_payload.get("page"),
                extra=metadata_payload.get("extra", {}),
            )
            chunk = DocumentChunk(
                id=item.get("id", ""),
                text=item.get("content", ""),
                metadata=metadata,
                embedding=item.get("embedding") or [],
            )
            score_value = item.get("similarity")
            if score_value is None:
                score_value = item.get("score")
            ranked.append(RankedChunk(chunk=chunk, score=score_value))
        return ranked
