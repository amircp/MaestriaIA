"""API del sistema RAG: /health, /ingest, /query """

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.chunk import chunk_text
from app.config import api_key, load_settings
from app.embed import GoogleEmbedder
from app.extract import extract_text, is_supported
from app.generate import ABSTAIN_TEXT, GeminiGenerator
from app.store import Hit, VectorStore


# --- Arranque: se crean los servicios una vez y viven en app.state --------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    app.state.settings = settings
    app.state.store = VectorStore(settings.chroma_path, settings.collection)
    key = api_key()
    # Sin clave la API arranca igual (para /health y /docs) y las rutas que
    # necesitan Google AI responden 503 con un mensaje claro.
    app.state.embedder = GoogleEmbedder(settings.embedding_model, key, settings.embed_batch) if key else None
    app.state.generator = GeminiGenerator(settings.generation_model, key) if key else None
    yield


app = FastAPI(
    title="RAG API de Amir",
    version="1.0.0",
    description=(
        "Ingesta documentos, los indexa en ChromaDB con embeddings de Google AI "
        "y responde preguntas con Gemini usando solo la evidencia recuperada."
    ),
    lifespan=lifespan,
)


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _embedder(request: Request) -> GoogleEmbedder:
    embedder = request.app.state.embedder
    if embedder is None:
        raise HTTPException(status_code=503, detail="Falta GOOGLE_API_KEY en .env: no se pueden calcular embeddings.")
    return embedder


def _generator(request: Request) -> GeminiGenerator:
    generator = request.app.state.generator
    if generator is None:
        raise HTTPException(status_code=503, detail="Falta GOOGLE_API_KEY en .env: no se puede generar la respuesta.")
    return generator



class HealthResponse(BaseModel):
    status: str
    api_key: bool = Field(description="Hay clave de Google AI en el entorno")
    chroma: bool = Field(description="La colección de Chroma responde")
    chunks: int | None = Field(description="Chunks indexados; None si Chroma no responde")
    sources: list[str] = Field(description="Archivos indexados")
    embedding_model: str
    generation_model: str
    top_k: int
    min_score: float


class IngestResponse(BaseModel):
    documents: int = Field(description="Documentos indexados en esta llamada")
    chunks: int = Field(description="Chunks indexados en esta llamada")
    sources: list[str] = Field(description="Archivos indexados en esta llamada")
    skipped: list[str] = Field(description="Archivos omitidos y por qué")


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, description="Pregunta del usuario")
    top_k: int | None = Field(default=None, ge=1, le=20, description="Chunks a recuperar (default: TOP_K)")
    source: str | None = Field(default=None, description="Buscar solo en este archivo")


class Citation(BaseModel):
    n: int = Field(description="Número con el que aparece citado en la respuesta")
    id: str = Field(description="Id del chunk en Chroma")
    source: str = Field(description="Archivo de origen")
    index: int = Field(description="Posición del chunk dentro del archivo")
    text: str = Field(description="Texto del chunk")
    score: float = Field(description="Similitud del coseno con la pregunta (1 = idéntico)")


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    abstained: bool = Field(description="True si no hubo evidencia suficiente")


class DeleteResponse(BaseModel):
    source: str
    deleted_chunks: int


# --- Tubería de ingesta (compartida por /ingest y /ingest/folder) --------------

def _index_document(request: Request, filename: str, data: bytes) -> int:
    """archivo -> texto -> chunks -> vectores -> Chroma. Devuelve chunks indexados."""
    settings = request.app.state.settings
    text = extract_text(filename, data)
    chunks = chunk_text(text, source=filename, size=settings.chunk_words, overlap=settings.chunk_overlap)
    if not chunks:
        return 0
    try:
        vectors = _embedder(request).embed_documents([c.text for c in chunks])
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Error de Google AI al incrustar: {exc}") from exc
    request.app.state.store.add(chunks, vectors)
    return len(chunks)


def _ingest_many(request: Request, items: list[tuple[str, bytes]]) -> IngestResponse:
    documents = 0
    chunks = 0
    sources: list[str] = []
    skipped: list[str] = []
    for filename, data in items:
        if not is_supported(filename):
            skipped.append(f"{filename}: formato no soportado (usa PDF, Markdown o texto)")
            continue
        try:
            n = _index_document(request, filename, data)
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001 - p. ej. PDF cifrado o corrupto
            skipped.append(f"{filename}: no se pudo leer ({exc})")
            continue
        if n == 0:
            skipped.append(f"{filename}: sin texto extraíble (¿PDF escaneado?)")
            continue
        documents += 1
        chunks += n
        sources.append(filename)
    return IngestResponse(documents=documents, chunks=chunks, sources=sources, skipped=skipped)


# --- Rutas ----------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["estado"])
def health(request: Request) -> HealthResponse:
    """Confirma que la API vive y reporta el estado del índice."""
    settings = request.app.state.settings
    try:
        chunks: int | None = request.app.state.store.count()
        sources = request.app.state.store.sources()
        chroma = True
    except Exception:  # noqa: BLE001
        chunks, sources, chroma = None, [], False
    return HealthResponse(
        status="ok",
        api_key=request.app.state.embedder is not None,
        chroma=chroma,
        chunks=chunks,
        sources=sources,
        embedding_model=settings.embedding_model,
        generation_model=settings.generation_model,
        top_k=settings.top_k,
        min_score=settings.min_score,
    )


@app.post("/ingest", response_model=IngestResponse, tags=["índice"])
async def ingest(
    request: Request,
    files: list[UploadFile] = File(description="PDF, Markdown o texto; varios a la vez"),
) -> IngestResponse:
    """Recibe archivos, los parte en chunks, los incrusta con Google AI y los guarda en Chroma."""
    items = [(f.filename or "sin-nombre", await f.read()) for f in files]
    return _ingest_many(request, items)


@app.post("/ingest/folder", response_model=IngestResponse, tags=["índice"])
def ingest_folder(request: Request) -> IngestResponse:
    """Indexa todos los documentos de la carpeta data/ (para cargar el corpus de golpe)."""
    root = Path(request.app.state.settings.data_path)
    if not root.is_dir():
        raise HTTPException(status_code=404, detail=f"No existe la carpeta de datos: {root}")
    paths = sorted(p for p in root.rglob("*") if p.is_file() and not p.name.startswith("."))
    items = [(str(p.relative_to(root)), p.read_bytes()) for p in paths]
    return _ingest_many(request, items)


@app.get("/sources", response_model=list[str], tags=["índice"])
def sources(request: Request) -> list[str]:
    """Archivos que hay en el índice."""
    return request.app.state.store.sources()


@app.delete("/sources/{source:path}", response_model=DeleteResponse, tags=["índice"])
def delete_source(request: Request, source: str) -> DeleteResponse:
    """Quita un archivo del índice sin reconstruir la colección."""
    deleted = request.app.state.store.delete_source(source)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No hay chunks de '{source}' en el índice.")
    return DeleteResponse(source=source, deleted_chunks=deleted)


@app.post("/query", response_model=QueryResponse, tags=["consulta"])
def query(request: Request, body: QueryRequest) -> QueryResponse:
    """Incrusta la pregunta, recupera los top-k chunks y pide a Gemini una respuesta anclada."""
    settings = request.app.state.settings
    store: VectorStore = request.app.state.store
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="La pregunta está vacía.")

    if store.count() == 0:
        return QueryResponse(
            answer="El índice está vacío: primero carga documentos.", citations=[], abstained=True
        )

    # 1) Recuperar
    try:
        vector = _embedder(request).embed_query(question)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Error de Google AI al incrustar la pregunta: {exc}") from exc
    hits: list[Hit] = store.search(vector, top_k=body.top_k or settings.top_k, source=body.source)
    citations = [
        Citation(n=n, id=h.id, source=h.source, index=h.index, text=h.text, score=round(h.score, 3))
        for n, h in enumerate(hits, start=1)
    ]

    # 2) Abstención por umbral: ningún chunk se parece lo suficiente a la pregunta.
    if not hits or hits[0].score < settings.min_score:
        return QueryResponse(answer=ABSTAIN_TEXT, citations=citations, abstained=True)

    # 3) Generar con la evidencia. El modelo también puede abstenerse si el
    #    contexto, aunque parecido, no responde la pregunta.
    try:
        answer, abstained = _generator(request).answer(question, hits)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Error de Google AI al generar: {exc}") from exc
    return QueryResponse(answer=answer, citations=citations, abstained=abstained)
