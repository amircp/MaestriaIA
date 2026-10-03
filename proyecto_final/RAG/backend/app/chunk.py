"""Partir un texto en fragmentos (chunks) de N palabras con solape.

Un chunk demasiado grande mete ruido en el prompt; uno demasiado chico
pierde el contexto que necesita la respuesta. El solape evita cortar una
idea justo en la frontera entre dos chunks.

Este módulo no usa red ni librerías: es la misma idea que el laboratorio
del curso, solo que aquí el tamaño se mide en palabras del documento real.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    source: str   # archivo de origen
    index: int    # posición dentro del documento: 0, 1, 2, ...
    text: str

    @property
    def id(self) -> str:
        return f"{self.source}#{self.index}"

    @property
    def word_count(self) -> int:
        return len(self.text.split())


def normalize(text: str) -> str:
    return " ".join(text.split())


def chunk_text(text: str, source: str, size: int = 300, overlap: int = 60) -> list[Chunk]:
    if size < 1:
        raise ValueError("size debe ser >= 1")
    if not 0 <= overlap < size:
        raise ValueError("overlap debe cumplir 0 <= overlap < size")

    words = normalize(text).split()
    if not words:
        return []

    step = size - overlap
    chunks: list[Chunk] = []
    start = 0
    index = 0
    while True:
        window = words[start : start + size]
        chunks.append(Chunk(source=source, index=index, text=" ".join(window)))
        if start + size >= len(words):  # esta ventana ya alcanzó el final
            break
        start += step
        index += 1
    return chunks
