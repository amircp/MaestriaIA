"""Sacar texto plano de un archivo: PDF, Markdown o texto."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

SUPPORTED = {".pdf", ".md", ".markdown", ".txt"}


def is_supported(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED


def extract_text(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        reader = PdfReader(BytesIO(data))
        pages = [(page.extract_text() or "") for page in reader.pages]
        return "\n".join(pages)
    if ext in SUPPORTED:
        return data.decode("utf-8", errors="replace")
    raise ValueError(
        f"Formato no soportado: '{ext or ''}'. Usa PDF, Markdown o texto."
    )
