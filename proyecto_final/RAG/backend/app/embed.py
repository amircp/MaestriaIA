"""Embeddings con Google AI."""

from __future__ import annotations

import time

from google import genai
from google.genai import types


RETRYABLE = ("429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE")


class GoogleEmbedder:
    def __init__(self, model: str, api_key: str, batch_size: int = 32) -> None:
        self.model = model
        self.batch_size = batch_size
        self._client = genai.Client(api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            vectors.extend(self._embed(batch, task_type="RETRIEVAL_DOCUMENT"))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], task_type="RETRIEVAL_QUERY")[0]

    def _embed(self, texts: list[str], task_type: str, retries: int = 3) -> list[list[float]]:
        config = types.EmbedContentConfig(task_type=task_type)
        for attempt in range(retries):
            try:
                response = self._client.models.embed_content(
                    model=self.model, contents=texts, config=config
                )
                return [list(e.values) for e in response.embeddings]
            except Exception as exc:  # noqa: BLE001 - reintentamos solo cuota/servicio
                transient = any(code in str(exc) for code in RETRYABLE)
                if not transient or attempt == retries - 1:
                    raise
                time.sleep(2**attempt)  # 1 s, 2 s, 4 s
        raise RuntimeError("unreachable")
