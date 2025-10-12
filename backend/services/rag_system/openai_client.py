from __future__ import annotations

from typing import Iterable, List, Sequence, Optional, Any

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
    """Thin wrapper around the OpenAI chat completion API with Function Calling support."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def complete(
        self,
        messages: Iterable[dict],
        *,
        temperature: float = 0.0,
        tools: Optional[List[dict]] = None,
        tool_choice: Optional[str | dict] = None
    ) -> str | dict:
        """
        Complete a chat conversation.

        Returns:
            - str: If no function call, returns the text response
            - dict: If function call detected, returns {'function_call': {...}, 'content': str}
        """
        kwargs = {
            "model": self._model,
            "messages": list(messages),
            "temperature": temperature,
        }

        if tools:
            kwargs["tools"] = tools
            # Use provided tool_choice (typically "auto" to let GPT decide)
            # Only set tool_choice if explicitly provided
            if tool_choice is not None:
                kwargs["tool_choice"] = tool_choice
            print(f"[DEBUG OpenAI] Sending tools to OpenAI: {tools}")
            print(f"[DEBUG OpenAI] Model: {self._model}")
            print(f"[DEBUG OpenAI] tool_choice: {kwargs.get('tool_choice', 'default (auto)')}")

        response = self._client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        print(f"[DEBUG OpenAI] Response message.content: {message.content[:100] if message.content else 'None'}")
        print(f"[DEBUG OpenAI] Response message.tool_calls: {message.tool_calls}")

        # Check for function/tool calls
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            return {
                "function_call": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                },
                "content": message.content or ""
            }

        return message.content or ""
