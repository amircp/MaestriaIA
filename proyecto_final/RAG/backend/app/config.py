"""Configuración leída del entorno.

Los valores vienen de docker-compose.yml (parámetros) y de .env (la clave).
Todo lo ajustable del sistema pasa por aquí, para que no haya números
mágicos repartidos por los módulos.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    chroma_path: str        # carpeta donde Chroma persiste el índice
    data_path: str          # carpeta con el corpus
    collection: str         # nombre de la colección en Chroma
    embedding_model: str    # el MISMO modelo para documentos y preguntas
    generation_model: str   # modelo que redacta la respuesta
    chunk_words: int        # palabras por chunk
    chunk_overlap: int      # palabras compartidas entre chunks vecinos
    top_k: int              # chunks recuperados por defecto
    min_score: float        # similitud mínima del mejor chunk para no abstenerse
    embed_batch: int        # chunks por llamada a Google AI


def load_settings() -> Settings:
    return Settings(
        chroma_path=os.getenv("CHROMA_PATH", "chroma"),
        data_path=os.getenv("DATA_PATH", "data"),
        collection=os.getenv("COLLECTION", "documentos"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
        generation_model=os.getenv("GENERATION_MODEL", "gemini-3.6-flash"),
        chunk_words=int(os.getenv("CHUNK_WORDS", "300")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "60")),
        top_k=int(os.getenv("TOP_K", "4")),
        min_score=float(os.getenv("MIN_SCORE", "0.5")),
        embed_batch=int(os.getenv("EMBED_BATCH", "32")),
    )


def api_key() -> str | None:
    """El SDK google-genai acepta cualquiera de las dos variables."""
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or None
