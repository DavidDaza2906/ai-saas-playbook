# Showcase — Guion de demostración

> **Playbook de IA Responsable para PYMES** · Global South AI Safety Hackathon 2026
> Demo: ~5 min · Paper: métricas al final

---

## Cómo levantar el sistema

```bash
# Terminal 1: backend (FastAPI + RAG)
cd app/backend && .venv/bin/uvicorn main:app --port 8000 --reload

# Terminal 2: frontend (Vite + React)
cd app/frontend && npm run dev

# Abrir http://localhost:5173
```

**Requisitos:** API key de OpenCode en `~/.local/share/opencode/auth.json` (opencode-go), API key de Voyage en `app/backend/.env`. Sin keys, corre en modo degradado (plantilla + BM25).

---

## Guion para jueces (~5 min)

### 0. Apertura (30s)
> "SaaS de autodiagnóstico de gobernanza de IA para PYMES. El sistema evalúa el uso de IA frente a NIST AI RMF, ISO 42001 y los 5 principios éticos consolidados (UNESCO/OCDE). Entrega tres capas: **diagnóstico determinista** (vector 3D), **recomendaciones priorizadas**, y **ejecución con RAG** que produce artefactos verificables. El diferenciador AI safety: **3 capas anti-alucinación** including faithfulness LLM-as-judge."

### 1. Wizard — botón "Cargar caso demo (POC)" (1 min)
- **Mostrar:** asistente de 4 pasos (contexto → bifurcación → árbol → resultados).
- **Caso POC:** PYME de comercio, ruta C (productos + procesos internos), 3 sistemas de IA, uno de alto riesgo (preselección de hojas de vida).
- **Puntos clave:**
  - Árbol de 34 preguntas (15 base + 19 subpreguntas condicionales).
  - Tipos de pregunta: opción múltiple, escala Likert, **numérico** (¿cuántos sistemas?), **matriz** (clasificar riesgo por sistema), texto abierto.
  - Subpreguntas aparecen según respuestas (ej. "¿usa datos personales? Sí" → activa consentimiento, DPIA, responsable de datos).
  - **Adjuntar evidencia:** el usuario puede subir PDF/DOCX/TXT en cualquier pregunta. El backend extrae el texto y devuelve un **score de cobertura** (% de palabras clave de la pregunta encontradas en el documento). Si supera el umbral, la respuesta se considera verificada con evidencia.

### 2. Pestaña "Vector 3D" (1 min)
- **Mostrar:** dashboard con 3 visualizaciones + gap register.
- **Puntos clave:**
  - **Espacio 3D interactivo (Plotly):** punto en (x=ÉTICO 25, y=ISO 27, z=NIST 28). Ejes 0-100. Rojo (<40), ámbar (40-70), verde (>70). Planos de referencia en 50 y 80.
  - **Radar NIST:** 4 puntas (GOVERN 38, MAP 43, MEASURE 20, MANAGE 32).
  - **Radar ético:** 5 puntas (beneficencia 12, no_maleficencia 25, autonomía 28, justicia 42, explicabilidad 43).
  - **Gap register:** 12 brechas (4 altas: A.5.1, A.6.2, A.9.2, A.5.3), ordenadas por severidad.
- **Narrativa:** "El diagnóstico es **determinista y reproducible** — mismas respuestas siempre dan el mismo vector. 360 tests lo verifican. El vector usa **promedio ponderado** con pesos congelados vía RAG en diseño."

### 3. Pestaña "Política + faithfulness" (1.5 min) — el diferenciador AI safety
- **Acción:** clic "Generar política con RAG" (toma ~1-2 min, hay spinner).
- **Mostrar mientras carga:** "Retrieval híbrido + LLM + verificación de faithfulness".
- **Puntos clave al terminar:**
  - **Política de IA generada** a la medida (~3500 chars), con **citas resaltadas** (ISO 42001, NIST AI RMF).
  - **Fuentes normativas recuperadas** (6 chunks con score de rerank).
  - **Verificación de citas (2ª capa):** "✓ Todas las citas son válidas" — 0 inválidas.
  - **Faithfulness LLM-as-judge (3ª capa):** score 0.83, 18 afirmaciones, 15 faithful, 1 unfaithful detectada. Expandir para mostrar la afirmación no respaldada con su explicación.
- **Narrativa:** "Tres capas anti-alucinación modelo queso suizo de Hendrycks: (1) retrieval con umbral de abstención, (2) validación determinista de citas contra el índice, (3) **faithfulness LLM-as-judge** que verifica entailment de cada afirmación. El sistema **no inventa**: si algo no está en las fuentes, lo detecta."

### 4. Pestaña "Artefactos" (1 min)
- **Acción:** clic "Generar artefactos" (instantáneo, determinista).
- **Mostrar:**
  - **Plan de implementación accionable (3.5):** 12 tareas agrupadas por fase (7 quick wins 0-30 días, 5 mediano plazo), cada una con responsable, esfuerzo, criterio de cierre. Botón "Descargar .md".
  - **Constancia verificable (3.6):** registro con fecha, organización, qué se evaluó/encontró/generó, marco normativo. Botón "Descargar .md".
- **Narrativa:** "El SaaS **produce, no solo aconseja**. La constancia es un activo comercial y regulatorio que la PYME puede presentar a clientes y auditorías para demostrar credibilidad en su uso de IA."

### 5. Cierre — robustez del diseño (30s)
> "360 tests unitarios + de coherencia verifican el motor determinista. El RAG combina retrieval híbrido con validación determinista de citas y faithfulness LLM-as-judge. Las métricas RAGAS se regenerarán con el corpus universal en la siguiente versión del paper."

---

## Robustez del diseño (anexo)

### 3 capas de defensa anti-alucinación (modelo queso suizo de Hendrycks)

| Capa | Mecanismo |
|------|-----------|
| **1. Retrieval + umbral** | Híbrido estructurado + BM25 + Voyage densa + RRF + rerank, abstención <0.35 |
| **2. Validación de citas** | Regex contra índice corpus + controls.json |
| **3. Faithfulness LLM-as-judge** | 2ª llamada LLM verifica entailment de cada afirmación |

### Suite de tests
- **360 tests** (motor + API + coherencia + regresión), **~1s**, sin red.
- 300 casos aleatorios × 9 invariantes = 2,700 checks, 0 incoherencias.
- Invariantes: bounded [0,100], severidad válida, gap_register ordenado, recs priorizadas, monotonicidad (mejorar respuestas nunca baja el score), reproducibilidad.

### Métricas RAGAS
> Pendientes de regeneración con el corpus normativo universal (NIST + ISO 42001 + principios éticos UNESCO/OCDE).

---

## Plan B — si algo falla en vivo

| Falla | Qué hacer |
|-------|-----------|
| Backend cae | Mostrar `INFORME_TECNICO.md` + `eval_report.md` (paper) |
| Voyage rate-limita (3 RPM) | Retrieval degrada a BM25+estructurado automáticamente (sigue funcionando, sin capa semántica) |
| Política tarda mucho (>2 min) | El frontend muestra spinner; si timeout, mostrar fallback plantilla |
| Frontend no renderiza Plotly | Mostrar capturas estáticas o el JSON del diagnóstico vía `/api/diagnose` |
| Sin internet / OpenCode sin créditos | Modo degradado: política de plantilla + retrieval BM25, demo sigue |

---

## Arquitectura (resumen para preguntas de jueces)

```
PYME responde wizard (34 preguntas)
        ↓
Motor determinista (engine.py) — sin LLM, sin red
        ↓
Diagnóstico: vector 3D (ÉTICO, ISO, NIST) + gap register + verificabilidad
        ↓
Recomendaciones: lookup brecha→control, priorizadas por riesgo/esfuerzo
        ↓
RAG (Capa 3): retrieval híbrido (Voyage + BM25 + estructurado)
        ↓
Generación: LLM (glm-5.2 vía OpenCode API) con prompt grounded-only
        ↓
3 capas anti-alucinación: umbral → citas validadas → faithfulness
        ↓
Artefactos: política + plan accionable + constancia verificable (descargables)
```

**Stack:** Python + FastAPI (backend) · Vite + React + TypeScript + Tailwind + Plotly (frontend) · OpenCode API glm-5.2 (LLM) · Voyage AI (embeddings + rerank). Sin base de datos (estado en sesión). Sin Anthropic SDK (cliente HTTP delgado a OpenCode).
