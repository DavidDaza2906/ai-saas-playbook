# ESTADO DEL PROYECTO Y TO-DO
> Playbook de IA Responsable para PYMES · Global South AI Safety Hackathon 2026
> Última actualización: 2026-06-21

## Resumen en una línea
Backend funcional con RAG completo (3 capas anti-alucinación + métricas RAGAS para el paper): motor determinista (Capa 1+2) + RAG (Capa 3) con API de OpenCode + Voyage; árbol real cargado con pesos congelados; métricas: recall@6=0.85, precisión citas=1.0, faithfulness=0.88. Falta el frontend.

---

## Decisiones de diseño tomadas (no relitigar)
- **Fuente de verdad:** `PROPUESTAFINAL.md`.
- **Marco ético:** 5 principios consolidados (Beneficencia, No maleficencia, Autonomía, Justicia, Explicabilidad) desde UNESCO + OCDE (Floridi). Corpus normativo universal: NIST AI RMF, ISO 42001 y principios éticos consolidados.
- **Ejes del diagnóstico:** **ÉTICO, NIST, ISO** (se eliminaron LEGAL y RESPONSABILIDAD como ejes; responsabilidad queda cubierta por NIST GOVERN + Explicabilidad). Se derivan del `mapeo` de cada pregunta (sin campo `eje`). El diagnóstico emite un **vector (x=ÉTICO, y=ISO, z=NIST)**, cada eje 0–100, para un **diagnóstico visual en espacio 3D**. Tablas de ejes de `PROPUESTAFINAL.md` y `SaaS.md` ya actualizadas a ÉTICO/NIST/ISO.
- **Scoring del vector:** promedio **ponderado** por eje, `eje = 100·Σ(aᵢ·wᵢ)/Σwᵢ`, normalizado sobre las preguntas efectivamente puntuadas (maneja ramas y "na"). Pesos `wᵢ` por eje: fijos en `pesos` o derivados del `mapeo` (binario) si faltan.
- **Pesos vía RAG, congelados:** se corren UNA vez con `propose_weights.py` (RAG propone los 60 pesos con justificación) → el equipo revisa y congela en `questions.json`. Runtime = determinista. El RAG no participa en cada sesión, solo en diseño.
- **Alcance demo:** marco normativo universal, sin paquete país activo.
- **Evidencia documental:** voluntaria (coherente con §6.3).
- **Principio rector:** el motor (reglas) decide; el RAG/LLM redacta. La lógica con consecuencia legal es determinista y auditable.
- **Stack:** backend Python + FastAPI; RAG = retrieval híbrido (estructurado + BM25 + denso Voyage + RRF + rerank + umbral abstención) + **API de OpenCode (glm-5.2)** para generación + verificador de citas. Frontend = Vite/React (pendiente).
- **LLM vía OpenCode (no Anthropic):** el RAG usa la API de OpenCode Go (`https://opencode.ai/zen/go/v1`) con la key de `~/.local/share/opencode/auth.json`. Sin key de Anthropic. Cliente en `rag/llm_client.py`.
- **Modelo LLM híbrido:** `glm-5.2` para generación de política (Capa 3, razonamiento, ~30s, calidad alta); `deepseek-v4-flash` configurado para tareas JSON estructuradas (`propose_weights.py`, uso futuro si se re-corre). Pesos ya congelados con glm-5.2 — no se regeneran.
- **Voyage activo:** embeddings `voyage-3` cacheados en disco (`data/cache/embeddings.json`, una sola vez) + rerank `rerank-2`. Capa gratuita (3 RPM) — degrada con elegancia a BM25+estructurado si rate-limit.
- **Modo degradado:** si no hay key de OpenCode, la política sale de plantilla; si no hay Voyage, retrieval usa estructurado+BM25. La demo nunca depende de la red.
- **Preguntas:** cerradas, opción múltiple, con valor fijo por opción. El motor normaliza por escala. **Árbol real cargado desde `ARBOL_PREGUNTAS.md`** (15 preguntas base + 19 subpreguntas = 34), con tipos `multiple`, `multiple_seleccion`, `likert`, `numero` (tramos), `matriz` (tabla por sistema) y `texto` (no puntúa). Subpreguntas anidadas con `condicion` sobre la respuesta del padre.
- **Fuente de verdad del árbol:** `ARBOL_PREGUNTAS.md` (aprobación humana). `PROPUESTAFINAL.md` es la fuente de la propuesta. El sistema se adaptó al árbol, no al revés.

---

## Estado del entorno
- [x] Python 3.14 + venv en `app/backend/.venv` con dependencias instaladas
- [x] `requirements.txt` congelado
- [ ] **Node/npm** (bloquea el frontend) → `sudo pacman -S nodejs npm`
- [x] **API de OpenCode** (glm-5.2) — key en `~/.local/share/opencode/auth.json` (opencode-go), auto-leída por `rag/llm_client.py`
- [x] **Voyage API key** en `.env` (embeddings + rerank; capa gratuita)
- [x] Embeddings del corpus cacheados en `data/cache/embeddings.json` (29 chunks, una sola vez)

---

## Estado por componente

### Documentos
- [x] `PROPUESTAFINAL.md` — propuesta (fuente de verdad)
- [x] `SaaS.md` — infraestructura operativa (alineada al marco nuevo)
- [x] `RAG.md` — guía de construcción del RAG
- [x] `app/backend/data/SCHEMA_PREGUNTAS.md` — contrato de las 20 preguntas

### Backend — núcleo determinista
- [x] Motor de diagnóstico (Capa 1) data-driven, sin IDs cableados
- [x] Motor de recomendaciones (Capa 2) por lookup + priorización
- [x] Carga de corpus universal (NIST + ISO 42001 + principios éticos UNESCO/OCDE)
- [x] Validador de preguntas (`validate_questions.py`)
- [x] Caso POC ejecutable (`poc.py`)
- [x] **Suite de tests** (`tests/test_engine.py` + `tests/test_api.py`): 23 tests, 0.29s, sin red

### Backend — RAG (Capa 3) — COMPLETO
- [x] Retriever híbrido con umbral de abstención (estructurado + BM25 + denso Voyage + RRF + rerank)
- [x] Embeddings del corpus cacheados en disco (una sola vez)
- [x] Generador de política (API OpenCode glm-5.2, con fallback plantilla)
- [x] Verificador de citas contra el índice (incluye controls.json) — 2ª capa anti-alucinación
- [x] **Verificador de faithfulness (LLM-as-judge)** — 3ª capa anti-alucinación (rag/faithfulness.py)
- [x] API FastAPI: `/health`, `/questions`, `/diagnose`, `/policy` (con `faithfulness=true`)
- [x] **Pesos congelados** en `questions.json` (30 preguntas, vía `propose_weights.py` + revisión)

### Evaluación RAGAS (para el paper) — COMPLETO
- [x] Golden set: 10 consultas con controles/citas esperados (`data/golden_set.json`)
- [x] Harness de evaluación paralelo (`eval_harness.py`): recall@k, precisión citas, faithfulness
- [x] **Métricas finales:** recall@6=0.85 · precisión citas=1.0 · faithfulness=0.88 (n=10)
- [x] Reporte markdown (`data/eval_report.md`) + JSON con detalle (`data/eval_result.json`)

### Datos / corpus
- [x] Corpus universal: NIST, ISO 42001, 5 principios éticos (UNESCO/OCDE)
- [x] Controles NIST/ISO + registro de principios (`controls.json`) — ampliado con A.5.1, A.5.3, A.8.5, A.10.3 y descripciones alineadas al árbol
- [x] Tabla de recomendaciones (`recommendations.json`) — 13 recs cubriendo todos los controles usados
- [x] **Árbol real cargado** (`questions.json`): 15 preguntas base + 19 subpreguntas, siguiendo `ARBOL_PREGUNTAS.md`

---

## TO-DO pendiente

### Insumo crítico (lo da el usuario)
- [x] **Cargar el árbol de preguntas real** desde `ARBOL_PREGUNTAS.md` — hecho (15 base + 19 subpreguntas)
- [x] **Congelar pesos:** `propose_weights.py` corrido con API de OpenCode → 30 pesos propuestos → congelados en `questions.json`. El vector 3D ya discrimina (ej. caso fuerte ético: ÉTICO 81 > ISO 77; caso fuerte ISO: ÉTICO 38 < ISO 43).

### Capa 3 — artefactos faltantes (orden de impacto/esfuerzo)
- [ ] 3.6 Constancia verificable (barato; datos ya existen)
- [ ] 3.5 Plan de implementación accionable (barato; estructura ya existe en Capa 2)
- [ ] 3.2 Registros operativos (inventario, matriz de riesgos, plantilla EIA)
- [ ] 3.3 Procedimientos · 3.4 Insumos de auditoría (SoA)

### Frontend
- [x] Scaffold Vite/React/TS
- [x] Wizard 4 pasos (contexto → bifurcación → árbol → resultados)
- [x] Dashboard: radar NIST, plano cartesiano, gap register, verificabilidad
- [x] Render de artefactos Capa 3 + descarga
- [x] Subida real de archivos + análisis heurístico de cobertura

### Mecanismos de seguridad (§6)
- [x] 6.1 Disclaimer visible en README y UI
- [x] 6.2 Fallback silencioso ante errores de créditos del LLM
- [x] 6.3 Extracción real de documentos subidos (PDF/DOCX/TXT) vía `evidence_analyzer.py`

### Decisiones abiertas (requieren input del usuario)
- [ ] Rol del RAG en Capa 2 (híbrido / generativo / 100% determinista) — en discusión
- [ ] Dimensión proveedor/usuario de los 5 principios: ¿activarla en el diagnóstico?
- [x] Corregir contradicción en el pitch de `PROPUESTAFINAL.md` (evidencia "obligatoria" vs voluntaria) → resuelto: evidencia voluntaria

### Validación con keys reales (hecho)
- [x] API de OpenCode confirmada: `https://opencode.ai/zen/go/v1/chat/completions`, modelo `glm-5.2`, UA `opencode/1.15.7`
- [x] Voyage confirmado: `voyage-3` (embeddings) + `rerank-2` (rerank); capa gratuita 3 RPM, degrada con elegancia
- [x] Umbral de abstención 0.35 calibrado (rerank scores reales 0.6-0.9 para relevantes)

---

## Cómo correr lo que hay
```bash
cd app/backend
.venv/bin/python poc.py                 # diagnóstico + recomendaciones (caso POC)
.venv/bin/python validate_questions.py  # valida el árbol de preguntas
.venv/bin/pytest tests/ -v              # 23 tests (motor + API), 0.29s, sin red
.venv/bin/python eval_harness.py --con-faithfulness --report  # métricas RAGAS (paper)
.venv/bin/uvicorn main:app --reload     # API en http://127.0.0.1:8000
```
