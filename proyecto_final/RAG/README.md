# Sistema RAG — Streamlit + FastAPI + ChromaDB + Google AI

Proyecto final de la materia de Inteligencia Artificial. Un sistema de
preguntas y respuestas sobre documentos propios: los documentos se parten en
fragmentos, se convierten en vectores con Google AI, se guardan en ChromaDB y,
ante una pregunta, se recuperan los fragmentos más parecidos y Gemini redacta
una respuesta usando solo esa evidencia, con citas `[n]`. Si no hay evidencia
suficiente, el sistema se abstiene.

```
Usuario → Streamlit (8501) → HTTP JSON → FastAPI (8000) → Google AI  (embeddings)
                                                        → ChromaDB   (índice persistente)
                                                        → Gemini     (respuesta con citas)
```

Streamlit nunca habla con Chroma ni con Google AI: solo con la API.

## Requisitos

- Docker y Docker Compose (o Python 3.12 para correrlo sin Docker).
- Una clave de Google AI Studio: https://aistudio.google.com/apikey

## Configurar la clave

```bash
cp .env.example .env
# edita .env y pega la clave:
# GOOGLE_API_KEY=AIza...
```

`.env` está en `.gitignore`. Nunca se sube al repositorio.

## Levantar con Docker

```bash
docker compose up --build
```

- Interfaz: http://localhost:8501
- API y documentación interactiva: http://localhost:8000/docs

Si el puerto 8000 o el 8501 están ocupados:

```bash
BACKEND_PORT=8010 FRONTEND_PORT=8511 docker compose up --build
```

El código de `backend/app` y `frontend/app.py` está montado como volumen:
los cambios se recargan sin reconstruir. Solo hay que reconstruir
(`--build`) si cambian los `requirements.txt`.

## Levantar sin Docker

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' ../.env | xargs)   # carga GOOGLE_API_KEY
CHROMA_PATH=chroma DATA_PATH=../data uvicorn app.main:app --reload --port 8000

# Frontend, en otra terminal
cd frontend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
API_URL=http://localhost:8000 streamlit run app.py
```

## Usar el sistema

1. Pon tus documentos (PDF, Markdown o texto) en `data/` y en la interfaz
   pulsa "Indexar la carpeta data/", o súbelos desde la pestaña Documentos.
2. En la pestaña Preguntar escribe una pregunta. La respuesta trae citas
   `[n]` y, desplegable, los fragmentos usados con su archivo y su similitud.
3. Una pregunta que el corpus no cubre produce una abstención explícita.

Lo mismo desde la terminal:

```bash
curl -s localhost:8000/health
curl -s -X POST localhost:8000/ingest/folder
curl -s -X POST localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question": "¿qué dice el documento sobre ...?", "top_k": 4}'
```

## Rutas de la API

| Ruta | Qué hace |
|---|---|
| `GET /health` | Estado: clave presente, Chroma responde, chunks y archivos indexados, modelos, umbral |
| `POST /ingest` | Recibe archivos (multipart), los parte, incrusta y guarda. Devuelve documentos, chunks, omitidos |
| `POST /ingest/folder` | Igual, con todo lo que haya en `data/` |
| `POST /query` | `{"question", "top_k"?, "source"?}` → `{"answer", "citations", "abstained"}` |
| `GET /sources` | Archivos en el índice |
| `DELETE /sources/{archivo}` | Quita un archivo del índice sin reconstruirlo |

Una pregunta fuera de dominio devuelve 200 con `abstained: true`, nunca 500.
Sin clave, las rutas que necesitan Google AI devuelven 503 con un mensaje claro.

## Cómo funciona por dentro

Cada módulo de `backend/app/` hace una sola cosa:

| Módulo | Responsabilidad |
|---|---|
| `extract.py` | Archivo → texto plano (pypdf para PDF; UTF-8 para Markdown y texto) |
| `chunk.py` | Texto → fragmentos de `CHUNK_WORDS` palabras con `CHUNK_OVERLAP` de solape. Id estable `archivo#índice` |
| `embed.py` | Textos → vectores con `gemini-embedding-001`, en lotes, con `task_type` documento/pregunta. El **mismo** modelo para ambos |
| `store.py` | ChromaDB persistente en `backend/chroma/`, espacio coseno. `score = 1 - distancia` |
| `generate.py` | Prompt con fragmentos numerados `[n]` + instrucción de responder solo con eso, en español, con citas. Gemini redacta |
| `main.py` | Orquesta: rutas, contratos y manejo de errores. Sin lógica propia |

Flujo de una consulta:

1. `embed_query(pregunta)` → vector de la pregunta.
2. `store.search(vector, top_k)` → fragmentos más parecidos con su score.
3. Si el mejor score es menor que `MIN_SCORE`, abstención sin llamar a Gemini.
4. Si no, `generator.answer(pregunta, fragmentos)` → texto con citas, o
   abstención si el modelo responde que el contexto no cubre la pregunta.

### Regla de abstención

Dos capas:

- **Umbral de similitud**: si ni el mejor fragmento se parece a la pregunta
  (`score < MIN_SCORE`, por defecto 0.6), no se genera nada. Los fragmentos
  cercanos se devuelven igual, marcados como insuficientes, para calibrar.
- **Criterio del modelo**: aun con fragmentos parecidos, si no contienen la
  respuesta, el prompt obliga a Gemini a escribir la marca
  `NO HAY EVIDENCIA SUFICIENTE` y la API responde `abstained: true`.

`MIN_SCORE` se calibra con preguntas reales del dominio y se ajusta en
`docker-compose.yml`. Con el corpus final y `gemini-embedding-001`, las tres
preguntas del dominio dieron un mejor score de 0.76 a 0.81 y una pregunta ajena
("¿cuánto cuesta un boleto de avión a Cancún?") dio 0.54 a 0.57: por eso el
umbral quedó en 0.6.
Con este modelo los scores nunca bajan a 0: un texto sin relación queda
alrededor de 0.5, no de 0.

## Parámetros

Todos viven en `docker-compose.yml` (servicio `backend`):

| Variable | Default | Significado |
|---|---|---|
| `EMBEDDING_MODEL` | `gemini-embedding-001` | Modelo de embeddings, documentos y preguntas |
| `GENERATION_MODEL` | `gemini-3.6-flash` | Modelo que redacta |
| `CHUNK_WORDS` | 300 | Palabras por fragmento |
| `CHUNK_OVERLAP` | 60 | Palabras compartidas entre fragmentos vecinos |
| `TOP_K` | 4 | Fragmentos recuperados por defecto |
| `MIN_SCORE` | 0.6 | Similitud mínima para no abstenerse |
| `EMBED_BATCH` | 32 | Fragmentos por llamada a Google AI |

## Estructura

```
docker-compose.yml
.env.example              GOOGLE_API_KEY= (copiar a .env)
reporte.md                reporte de una página
evidencias/               capturas y respuestas JSON de las preguntas de prueba
data/                     corpus (se monta en el backend)
backend/
  Dockerfile, requirements.txt
  app/  config.py extract.py chunk.py embed.py store.py generate.py main.py
  chroma/                 índice persistente (en .gitignore)
frontend/
  Dockerfile, requirements.txt
  app.py                  Streamlit: estado, carga, chat, citas, scores
```

## Entrega

El enunciado sugiere `RAG/Proyecto final/` en el repo del curso; esta entrega
vive en `Ejercicios/proyecto_final/RAG/` de mi repo propio (el enunciado permite
otra subcarpeta si se documenta).

- **Corpus**: `data/`, 9 trabajos propios de estadística y minería de datos
  (8,064 palabras, 35 chunks). Se indexa con "Indexar la carpeta data/" en la
  UI o con `POST /ingest/folder`.
- **Reporte**: `reporte.md` (dominio y tamaño del corpus, partición,
  abstención, qué hace Google AI y qué hace Chroma).
- **Evidencias**: `evidencias/`
  - `01_streamlit_citas.png`: respuesta con citas y scores en Streamlit.
  - `02_docs_query.png`: la misma pregunta en `/docs`.
  - `03_abstencion.png`: pregunta fuera de dominio, el sistema se abstiene.
  - `01_…json` a `05_…json`: respuestas completas de las cinco preguntas de prueba.
