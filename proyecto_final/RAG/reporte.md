# Proyecto final — Sistema RAG sobre trabajos de estadística y minería de datos

Amir Oswaldo Canto Palomo · Inteligencia Artificial

## 1. Dominio y tamaño del corpus

Los datos indexados corresponden a **9 trabajos propios** de la Especialidad en Estadística (UADY) y de esta materia: minería de
datos, análisis multivariado, diseño de experimentos, regresión y clustering. Todos son de mi autoría
(la exposición de Dunnett, en equipo), así que se pueden compartir en la entrega.

| Documento | Palabras | Chunks |
|---|---:|---:|
| `cheatsheet-clustering.md` | 2,912 | 12 |
| `multivariado-actividad2-analisis-descriptivo.pdf` | 1,133 | 5 |
| `mineria-proyecto-final-arboles-decision.pdf` | 992 | 4 |
| `ia-kmedias-reporte.md` | 977 | 4 |
| `disexp-exposicion1-comparacion-control.pdf` | 606 | 3 |
| `mineria-regresion-multiple-esperanza-vida.pdf` | 541 | 3 |
| `mineria-actividad1-tecnicas.pdf` | 387 | 2 |
| `mineria-actividad8-descriptivo-pts.pdf` | 298 | 1 |
| `mineria-actividad7-reduccion-dimensionalidad.pdf` | 218 | 1 |
| **Total** | **8,064** | **35** |

Modelo de embeddings: **`gemini-embedding-001`** (vectores de 3,072 dimensiones). Generación: **`gemini-3.6-flash`**.

## 2. Partición

Chunks de **300 palabras con 60 de solape** (20 %), dentro del rango sugerido (200–400 / 40–80).
Los documentos son reportes cortos (218 a 2,912 palabras) organizados por secciones; 300 palabras
equivalen más o menos a una sección completa (por ejemplo, "Modelo 5 + validación de supuestos" de la
regresión cae en un solo chunk), así que cada fragmento trae el dato y su contexto. El solape de 60
palabras evita que una idea quede partida justo en la frontera. Los dos documentos más cortos quedan en
un solo chunk.

## 3. Cómo decide abstenerse

Hay dos capas:

1. **Umbral de similitud (`MIN_SCORE = 0.6`)**: si el mejor chunk tiene similitud coseno menor a 0.6, la
   API responde "no tengo suficiente conocimiento" sin llamar a Gemini. Con este corpus las preguntas del
   dominio dieron un mejor score de **0.76–0.81** y una pregunta ajena ("¿Cuánto cuesta un boleto de avión
   a Cancún?") dio **0.573**; con `gemini-embedding-001` un texto sin relación queda cerca de 0.5, no de 0.
2. **Criterio del modelo**: si los chunks se parecen pero no contienen la respuesta, el prompt obliga a
   Gemini a escribir `NO HAY EVIDENCIA SUFICIENTE` y la API marca `abstained: true`. Ejemplo: "¿Qué
   exactitud obtuvo una red neuronal en la base de tumores?" recupera el proyecto de tumores con score
   **0.707** (pasa el umbral), pero ese proyecto usó árboles de decisión, y Gemini se abstiene.

| Pregunta | Mejor score | Resultado |
|---|---:|---|
| Variables y R² del modelo final de esperanza de vida | 0.792 | Asesinatos, universitarios, heladas; R² = 0.7127 [1][2] |
| Componentes conservados en U2ppg2008 | 0.762 | 8 componentes (PC1–PC8), 90 % de varianza acumulada [1] |
| k sugerido por la silueta tras separar los blobs | 0.808 | k = 5 con 0.777 [1] |
| Boleto de avión a Cancún | 0.573 | Abstención por umbral |
| Exactitud de una red neuronal en tumores | 0.707 | Abstención por el modelo |

## 4. Qué hace Google AI y qué hace Chroma

- **Google AI, embeddings**: convierte cada chunk (`task_type = RETRIEVAL_DOCUMENT`) y cada pregunta
  (`RETRIEVAL_QUERY`) en un vector, con el **mismo** modelo para ambos.
- **Google AI, generación**: Gemini recibe los chunks numerados `[1]…[k]` y redacta la respuesta en
  español, citando cada afirmación y usando solo esa evidencia.
- **ChromaDB**: guarda cada chunk con su vector, su texto y sus metadatos (`source`, `index`) en una
  colección persistente en disco (espacio coseno), y devuelve los `top_k = 4` vecinos más cercanos. No usa
  su embedder por defecto: recibe los vectores ya calculados por Google AI.

Evidencias en `evidencias/`: `01_streamlit_citas.png`, `02_docs_query.png`, `03_abstencion.png` y las
respuestas JSON de las cinco preguntas.

Adicionalmente incluyo ARQUITECTURA.html generado con IA para visualizar un diagrama de arquitectura de la plataforma.


PD: saludos Profe! gracias por su materia, fue excelente!