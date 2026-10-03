"""Interfaz del sistema RAG."""

from __future__ import annotations

import os

import httpx
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = httpx.Timeout(120.0, connect=5.0)  # ingestar un PDF grande tarda

st.set_page_config(page_title="Proyecto Final Amir", page_icon="😎", layout="wide")


def api(method: str, path: str, **kwargs) -> httpx.Response | None:
    """Llama a la API. Si no responde, muestra el error y devuelve None."""
    try:
        return httpx.request(method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs)
    except httpx.ConnectError:
        st.error(f"No se puede conectar con la API en {API_URL}. ¿Está corriendo el backend?")
    except httpx.TimeoutException:
        st.error("La API tardó demasiado en responder. Intenta de nuevo.")
    return None


def detail(response: httpx.Response) -> str:
    try:
        return str(response.json().get("detail", response.text))
    except ValueError:
        return response.text


health = None
with st.sidebar:
    st.title("😎 RAG Amir")
    r = api("GET", "/health")
    if r is not None and r.status_code == 200:
        health = r.json()
        st.success("API conectada")
        if not health["api_key"]:
            st.warning("Falta GOOGLE_API_KEY en el .env del backend.")
        if not health["chroma"]:
            st.error("ChromaDB no responde.")
        st.metric("Chunks indexados", health["chunks"] if health["chunks"] is not None else "?")
        st.caption(f"Embeddings: `{health['embedding_model']}`")
        st.caption(f"Generación: `{health['generation_model']}`")
        st.caption(f"Umbral de abstención: {health['min_score']}")
    elif r is not None:
        st.error(f"La API respondió {r.status_code}: {detail(r)}")

    st.divider()
    st.subheader("Parámetros de consulta")
    top_k = st.slider("Chunks a recuperar (top-k)", 1, 10, health["top_k"] if health else 4, key="top_k")
    sources = health["sources"] if health else []
    source = st.selectbox("Buscar solo en", ["Todos los documentos", *sources], key="source")
    source_filter = None if source == "Todos los documentos" else source

if health is None:
    st.stop()  # sin API no hay nada que mostrar


tab_preguntar, tab_documentos = st.tabs(["Preguntar", "Documentos"])


with tab_documentos:
    st.subheader("Cargar documentos")
    st.caption("PDF, Markdown o texto se convierten en embeddings e incrustan con Google AI y se guardan en ChromaDB.")
    uploaded = st.file_uploader(
        "Archivos", type=["pdf", "md", "txt"], accept_multiple_files=True, key="uploader"
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Indexar archivos", disabled=not uploaded, key="btn_ingest"):
            files = [("files", (f.name, f.getvalue(), f.type or "application/octet-stream")) for f in uploaded]
            with st.spinner("Incrustando e indexando..."):
                r = api("POST", "/ingest", files=files)
            if r is not None and r.status_code == 200:
                body = r.json()
                st.success(f"Indexados {body['documents']} documentos en {body['chunks']} chunks.")
                for s in body["skipped"]:
                    st.warning(f"Omitido: {s}")
                st.rerun()
            elif r is not None:
                st.error(detail(r))
    with col2:
        if st.button("Indexar la carpeta data/ del backend", key="btn_folder"):
            with st.spinner("Indexando la carpeta..."):
                r = api("POST", "/ingest/folder")
            if r is not None and r.status_code == 200:
                body = r.json()
                st.success(f"Indexados {body['documents']} documentos en {body['chunks']} chunks.")
                for s in body["skipped"]:
                    st.warning(f"Omitido: {s}")
                st.rerun()
            elif r is not None:
                st.error(detail(r))

    st.subheader("En el índice")
    if not sources:
        st.info("El índice está vacío. Carga documentos a la DB.")
    for s in sources:
        c1, c2 = st.columns([5, 1])
        c1.write(f"📄 {s}")
        if c2.button("Quitar", key=f"del_{s}"):
            r = api("DELETE", f"/sources/{s}")
            if r is not None and r.status_code == 200:
                st.rerun()
            elif r is not None:
                st.error(detail(r))


with tab_preguntar:
    if not sources:
        st.info("Todavía no hay documentos indexados. Ve a la pestaña Documentos.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("abstained"):
                    st.warning("El sistema se abstuvo: no encontró evidencia suficiente en los documentos.")
                cites = msg.get("citations", [])
                if cites:
                    label = "Fragmentos usados" if not msg.get("abstained") else "Fragmentos más cercanos (insuficientes)"
                    with st.expander(f"{label} ({len(cites)})"):
                        for c in cites:
                            st.markdown(f"**[{c['n']}] {c['source']}** · fragmento {c['index']} · similitud {c['score']:.3f}")
                            st.caption(c["text"])

    question = st.chat_input("Escribe tu pregunta")
    if question is not None:
        question = question.strip()
        if not question:
            st.warning("Escribe una pregunta antes de enviar.")
        else:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Buscando evidencia y redactando..."):
                    payload = {"question": question, "top_k": top_k}
                    if source_filter:
                        payload["source"] = source_filter
                    r = api("POST", "/query", json=payload)
                if r is None:
                    st.stop()
                if r.status_code != 200:
                    st.error(f"La API respondió {r.status_code}: {detail(r)}")
                    st.stop()
                body = r.json()
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": body["answer"],
                        "citations": body["citations"],
                        "abstained": body["abstained"],
                    }
                )
                st.rerun()
