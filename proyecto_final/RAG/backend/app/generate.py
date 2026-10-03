from __future__ import annotations

import time

from google import genai
from google.genai import types

from app.store import Hit

RETRYABLE = ("429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE")  # cuota o alta demanda: reintentar

ABSTAIN_MARK = "NO HAY EVIDENCIA SUFICIENTE"
ABSTAIN_TEXT = "No tengo suficiente conocimiento para responder esa pregunta."

SYSTEM_PROMPT = f"""Eres un asistente que responde preguntas usando únicamente la evidencia proporcionada.

Reglas:
1. Responde en español, de forma clara y breve.
2. Usa solo la información del contexto. No agregues conocimiento propio ni supongas datos.
3. Cita la evidencia con el número del fragmento entre corchetes, por ejemplo [1] o [2],
   justo después de la afirmación que apoya. Cada afirmación debe tener su cita.
4. Si el contexto no contiene la información necesaria, escribe exactamente: {ABSTAIN_MARK}
"""


def build_prompt(question: str, hits: list[Hit]) -> str:
    lines = ["Contexto:"]
    for n, hit in enumerate(hits, start=1):
        lines.append(f"[{n}] (fuente: {hit.source}, fragmento {hit.index})")
        lines.append(hit.text)
        lines.append("")
    lines.append(f"Pregunta: {question}")
    return "\n".join(lines)


class GeminiGenerator:
    def __init__(self, model: str, api_key: str, temperature: float = 0.2) -> None:
        self.model = model
        self.temperature = temperature
        self._client = genai.Client(api_key=api_key)

    def answer(self, question: str, hits: list[Hit]) -> tuple[str, bool]:
        """Devuelve (texto, abstained)."""
        response = self._generate(build_prompt(question, hits))
        texto = _text_of(response).strip()
        if not texto or ABSTAIN_MARK in texto.upper():
            return ABSTAIN_TEXT, True
        return texto, False


    def _generate(self, prompt: str, retries: int = 3):
        config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=self.temperature)
        for intento in range(retries):
            try:
                return self._client.models.generate_content(model=self.model, contents=prompt, config=config)
            except Exception as exc:  # noqa: BLE001 - reintentamos solo cuota/servicio
                validacion = any(code in str(exc) for code in RETRYABLE)
                if not validacion or intento == retries - 1:
                    raise
                time.sleep(2**intento)  # 1 s, 2 s, 4 s
        raise RuntimeError("unreachable")


def _text_of(response) -> str:
    """Junta solo las partes de texto"""
    candidatos = response.candidates or []
    if not candidatos or candidatos[0].content is None:
        return ""
    parts = candidatos[0].content.parts or []
    return "".join(part.text for part in parts if getattr(part, "text", None))
