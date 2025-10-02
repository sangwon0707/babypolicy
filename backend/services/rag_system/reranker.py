from __future__ import annotations

"""Cross-encoder based reranker used to reorder vector-store candidates."""

from typing import List, Sequence

try:  # pragma: no cover - optional dependency
    from sentence_transformers import CrossEncoder
except ImportError:  # pragma: no cover
    CrossEncoder = None  # type: ignore[misc]

from .vector_store import RankedChunk


class CrossEncoderReranker:
    """Wrap a sentence-transformers CrossEncoder for optional reranking."""

    def __init__(self, model_name: str, *, device: str | None = None) -> None:
        if CrossEncoder is None:
            raise ImportError(
                "sentence-transformers 패키지가 설치되어 있지 않습니다. "
                "리랭킹을 사용하려면 해당 패키지를 설치하세요."
            )
        self._model_name = model_name
        self._encoder = CrossEncoder(model_name, device=device)

    def rerank(
        self,
        question: str,
        candidates: Sequence[RankedChunk],
        *,
        top_n: int | None = None,
    ) -> List[RankedChunk]:
        """Return candidates sorted by cross-encoder score."""
        if not candidates:
            return []

        pairs = [(question, item.chunk.text) for item in candidates]
        scores = self._encoder.predict(pairs)

        reranked: List[RankedChunk] = [
            RankedChunk(chunk=item.chunk, score=float(score))
            for item, score in zip(candidates, scores, strict=True)
        ]
        reranked.sort(key=lambda item: (item.score or 0.0), reverse=True)

        if top_n is not None:
            reranked = reranked[: top_n]
        return reranked
