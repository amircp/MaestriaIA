"""Índice vectorial persistente con ChromaDB."""

from __future__ import annotations

from dataclasses import dataclass

import chromadb

from app.chunk import Chunk


@dataclass(frozen=True)
class Hit:
    id: str
    source: str
    index: int
    text: str
    score: float  # similitud del coseno con la pregunta


class VectorStore:
    def __init__(self, path: str, collection: str = "documentos") -> None:
        self._client = chromadb.PersistentClient(path=path)
        self._collection = self._client.get_or_create_collection(
            name=collection,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks y vectors deben tener la misma longitud")
        if not chunks:
            return
        # upsert: si el id ya existe (mismo archivo reindexado) se reemplaza.
        self._collection.upsert(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            embeddings=vectors,
            metadatas=[{"source": c.source, "index": c.index} for c in chunks],
        )

    def search(self, vector: list[float], top_k: int, source: str | None = None) -> list[Hit]:
        total = self.count()
        if total == 0:
            return []
        extra = {"where": {"source": source}} if source else {}
        result = self._collection.query(
            query_embeddings=[vector],
            n_results=min(top_k, total),
            include=["documents", "metadatas", "distances"],
            **extra,
        )
        hits: list[Hit] = []
        for id_, text, meta, dist in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            hits.append(
                Hit(id=id_, source=str(meta["source"]), index=int(meta["index"]), text=text, score=1.0 - dist)
            )
        return hits

    def count(self) -> int:
        return self._collection.count()

    def sources(self) -> list[str]:
        """Archivos distintos que hay en el índice."""
        metas = self._collection.get(include=["metadatas"])["metadatas"] or []
        return sorted({str(m["source"]) for m in metas})

    def delete_source(self, source: str) -> int:
        """Borra los chunks de un archivo sin tocar el resto. Devuelve cuántos quitó."""
        before = self.count()
        self._collection.delete(where={"source": source})
        return before - self.count()
