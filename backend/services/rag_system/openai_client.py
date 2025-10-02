from __future__ import annotations

from typing import Iterable, List, Sequence

from openai import OpenAI

try:  # pragma: no cover - optional dependency for local embeddings
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover
    SentenceTransformer = None  # type: ignore[assignment]


class OpenAIEmbeddingClient:
    """Wrapper that supports OpenAI embeddings and optional sentence-transformers fallback."""

    def __init__(self, api_key: str, model: str) -> None:
        self._model = model
        self._backend = "openai"
        self._client: OpenAI | None = None
        self._st_model: SentenceTransformer | None = None

        if self._should_use_sentence_transformers(model):
            if SentenceTransformer is None:
                raise ImportError("sentence-transformers 패키지가 설치되어 있지 않습니다.")
            self._backend = "sentence_transformers"
            self._st_model = SentenceTransformer(model)
        else:
            self._client = OpenAI(api_key=api_key)

    @staticmethod
    def _should_use_sentence_transformers(model: str) -> bool:
        return "/" in model or model.startswith("local:")

    def embed(self, inputs: Sequence[str]) -> List[List[float]]:
        if self._backend == "sentence_transformers":
            assert self._st_model is not None
            texts = [text if text.strip() else "" for text in inputs]
            if not any(texts):
                return [[] for _ in inputs]
            embeddings = self._st_model.encode(texts, normalize_embeddings=True)
            return [list(map(float, vector)) for vector in embeddings]

        # OpenAI backend (default)
        assert self._client is not None
        batched = [item for item in inputs if item.strip()]
        if not batched:
            return [[] for _ in inputs]
        response = self._client.embeddings.create(model=self._model, input=batched)
        embeddings = [item.embedding for item in response.data]

        iterator = iter(embeddings)
        result: List[List[float]] = []
        for text in inputs:
            if text.strip():
                result.append(next(iterator))
            else:
                result.append([])
        return result


class OpenAIChatClient:
    """Thin wrapper around the OpenAI chat completion API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def complete(self, messages: Iterable[dict], *, temperature: float = 0.0) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=list(messages),
            temperature=temperature,
        )
        message = response.choices[0].message
        return message.content or ""
