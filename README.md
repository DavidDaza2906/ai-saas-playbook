# Playbook de IA Responsable para PYMES

> **Global South AI Safety Hackathon 2026** · Track 1: Latinoamérica · Gobernanza
>
> SaaS de autodiagnóstico de gobernanza de IA para PYMES. Evalúa el uso de IA frente a NIST AI RMF, ISO 42001 y los 5 principios éticos consolidados (UNESCO + OCDE). Entrega diagnóstico determinista (vector 3D), recomendaciones priorizadas, y ejecución con RAG que produce artefactos verificables.

---

## Tabla de contenidos

- [Qué hace](#qué-hace)
- [Arquitectura](#arquitectura)
- [Stack técnico](#stack-técnico)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Endpoints de la API](#endpoints-de-la-api)
- [Tests](#tests)
- [Métricas RAGAS (paper)](#métricas-ragas-paper)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Documentación](#documentación)

---

## Qué hace

El sistema evalúa a una PYME en 3 capas:

| Capa | Qué produce | Naturaleza |
|------|-------------|-----------|
| **1. Diagnóstico** | Vector 3D (ÉTICO, ISO, NIST) + gap register + verificabilidad | Determinista (reglas) |
| **2. Recomendaciones** | Hoja de ruta priorizada con justificación normativa | Determinista (lookup) |
| **3. Ejecución (RAG)** | Política de IA generada a la medida + plan accionable + constancia verificable | Generativa (LLM + retrieval) |

**Diferenciador AI safety:** 3 capas anti-alucinación (modelo queso suizo de Hendrycks):
1. Retrieval con umbral de abstención
2. Validación determinista de citas contra el índice
3. Faithfulness LLM-as-judge (verifica entailment de cada afirmación)

---

## Arquitectura

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
Artefactos: política + plan accionable + constancia verificable + informe PDF
```

---

## Stack técnico

| Componente | Tecnología |
|-----------|-----------|
| Backend | Python 3.14 + FastAPI + uvicorn |
| Frontend | Vite + React + TypeScript + Tailwind v4 + Plotly + Recharts |
| LLM | OpenCode Go API (`glm-5.2`) — sin Anthropic SDK |
| Embeddings + rerank | Voyage AI (`voyage-3` + `rerank-2`) |
| PDF | WeasyPrint (HTML→PDF) |
| Tests | pytest (360 tests) |
| Sin base de datos | Estado solo en sesión |

---

## Requisitos

- **Python 3.12+** (probado con 3.14)
- **Node.js 20+** y npm (para el frontend)
- **API key de OpenCode** — se lee automáticamente de `~/.local/share/opencode/auth.json` (cuenta opencode-go), o definir `OPENCODE_API_KEY` en `.env`
- **API key de Voyage AI** — opcional (sin ella, degrada a BM25+estructurado). Capa gratuita en https://dash.voyageai.com
- **WeasyPrint** requiere `pango` y `cairo` instalados en el sistema (en Arch: `sudo pacman -S pango cairo`)

---

## Instalación

### 1. Clonar

```bash
git clone https://github.com/DavidDaza2906/ai-saas-playbook.git
cd ai-saas-playbook
```

### 2. Backend

```bash
cd app/backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install weasyprint fpdf2  # para informe PDF
cp .env.example .env
# Editar .env y añadir VOYAGE_API_KEY (opcional)
# OPENCODE_API_KEY se lee de auth.json automáticamente
```

### 3. Frontend

```bash
cd app/frontend
npm install
```

---

## Uso

### Levantar el sistema

```bash
# Terminal 1: backend
cd app/backend
.venv/bin/uvicorn main:app --port 8000 --reload

# Terminal 2: frontend
cd app/frontend
npm run dev
```

Abrir **http://localhost:5173**

### Demo rápida

1. Clic en **"Cargar caso demo (POC)"** — precarga una PYME de comercio con 3 sistemas de IA
2. Ver el diagnóstico: vector 3D, radares NIST/ISO/ética, gap register
3. Al final del informe, elegir "Necesito ayuda para implementar" → desbloquea política + artefactos
4. Generar política con RAG (~1-2 min) — ver citas + sello de verificación
5. Generar artefactos — plan accionable + constancia verificable (descargables)
6. Descargar informe PDF completo

### Sin frontend (API sola)

```bash
cd app/backend
.venv/bin/python poc.py                    # caso POC por Capa 1 + 2
.venv/bin/python validate_questions.py     # validar el árbol de preguntas
.venv/bin/python -m pytest tests/ -v       # 360 tests
```

---

## Endpoints de la API

| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado y capacidades activas (LLM, Voyage) |
| GET | `/api/questions` | Árbol de preguntas (15 base + 19 subpreguntas) |
| POST | `/api/diagnose` | Diagnóstico (Capa 1) + recomendaciones (Capa 2) |
| POST | `/api/policy` | Política de IA con RAG + faithfulness (Capa 3) |
| POST | `/api/artifacts` | Plan accionable (3.5) + constancia verificable (3.6) |
| POST | `/api/informe` | Informe PDF descargable (WeasyPrint) |

---

## Tests

```bash
cd app/backend
.venv/bin/python -m pytest tests/ -v
```

**360 tests** en 0.6s (sin red):

| Suite | Tests | Qué cubre |
|-------|-------|-----------|
| `test_engine.py` | 29 | Motor: reproducibilidad, edge cases, tipos, ramas, regresión |
| `test_api.py` | 5 | API: health, questions, diagnose, artifacts |
| `test_coherencia.py` | 326 | 300 casos aleatorios × 9 invariantes + monotonicidad + derivación |

---

## Métricas RAGAS (paper)

Evaluación sobre 10 consultas-oro (`data/golden_set.json`):

| Métrica | Resultado | Qué mide |
|---------|-----------|----------|
| **Recall@6** | 0.85 | % de fuentes esperadas recuperadas |
| **Precisión de citas** | 1.0 | 0 citas inválidas (2ª capa) |
| **Faithfulness** | 0.884 | % afirmaciones respaldadas por fuentes (3ª capa) |

```bash
cd app/backend
.venv/bin/python eval_harness.py --con-faithfulness --report
# Resultado: data/eval_report.md + data/eval_result.json
```

---

## Estructura del proyecto

```
ai-saas-playbook/
├── app/
│   ├── backend/
│   │   ├── engine.py                 # motor determinista (Capa 1 + 2)
│   │   ├── main.py                   # API FastAPI
│   │   ├── artifacts.py              # plan accionable + constancia (3.5 + 3.6)
│   │   ├── informe_pdf.py            # generador PDF (WeasyPrint)
│   │   ├── propose_weights.py        # pesos congelados vía RAG (una sola vez)
│   │   ├── validate_questions.py     # validador del árbol
│   │   ├── eval_harness.py           # harness RAGAS (métricas paper)
│   │   ├── poc.py                    # caso de prueba end-to-end
│   │   ├── rag/
│   │   │   ├── llm_client.py         # cliente OpenCode API
│   │   │   ├── retriever.py          # retrieval híbrido (estructurado + BM25 + Voyage + RRF + rerank)
│   │   │   ├── generator.py          # generación de política (Capa 3)
│   │   │   ├── verifier.py           # validación de citas (2ª capa anti-alucinación)
│   │   │   └── faithfulness.py       # verificador LLM-as-judge (3ª capa)
│   │   ├── data/
│   │   │   ├── questions.json        # árbol (15 base + 19 subpreguntas, pesos congelados)
│   │   │   ├── controls.json         # controles ISO 42001 + principios éticos
│   │   │   ├── recommendations.json  # lookup brecha → recomendación
│   │   │   ├── corpus/               # chunks normativos con metadatos
│   │   │   ├── golden_set.json       # 10 consultas-oro para evaluación
│   │   │   ├── eval_result.json      # resultados del harness
│   │   │   ├── eval_report.md        # reporte de métricas
│   │   │   └── SCHEMA_PREGUNTAS.md   # contrato del árbol
│   │   └── tests/
│   │       ├── test_engine.py        # tests del motor
│   │       ├── test_api.py           # tests de la API
│   │       └── test_coherencia.py    # tests de coherencia (300 casos)
│   └── frontend/
│       └── src/
│           ├── App.tsx               # orquestador + flujo procedural
│           ├── api.ts                # cliente API
│           ├── types.ts              # tipos TypeScript
│           └── components/
│               ├── Wizard.tsx        # asistente de 4 pasos
│               ├── Vector3D.tsx      # espacio 3D + radares + gap register
│               ├── PoliticaPanel.tsx # política (guía limpia)
│               ├── VerificacionTecnica.tsx  # métricas técnicas (jueces)
│               └── ...
├── PROPUESTAFINAL.md                 # propuesta (fuente de verdad)
├── ARBOL_PREGUNTAS.md                # árbol de preguntas (aprobación humana)
├── SaaS.md                           # infraestructura operativa
├── RAG.md                            # guía de construcción del RAG
├── INFORME_TECNICO.md                # informe técnico (anexo del paper)
├── ESTADO.md                         # estado del proyecto
└── app/SHOWCASE.md                   # guion de demostración
```

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [`PROPUESTAFINAL.md`](PROPUESTAFINAL.md) | Propuesta del proyecto (fuente de verdad) |
| [`ARBOL_PREGUNTAS.md`](ARBOL_PREGUNTAS.md) | Árbol de preguntas con aprobación humana |
| [`SaaS.md`](SaaS.md) | Infraestructura operativa del SaaS |
| [`RAG.md`](RAG.md) | Guía de construcción del RAG |
| [`INFORME_TECNICO.md`](INFORME_TECNICO.md) | Informe técnico (anexo del paper) |
| [`app/SHOWCASE.md`](app/SHOWCASE.md) | Guion de demostración para jueces |
| [`ESTADO.md`](ESTADO.md) | Estado del proyecto y TO-DO |

---

## AVISO DE CONFIDENCIALIDAD Y RESERVA DE DERECHOS

Este repositorio y todo su contenido (código fuente, documentación, metodología, estructura del cuestionario, esquemas de mapeo normativo y demás materiales) constituyen información confidencial y propiedad intelectual de David Daza Jaimes, Diana Daza Jaimes, Juan Camilo Medina Moreno, Luis Carlos Ordóñez Montenegro y Ángela Pinilla Parra. Todos los derechos quedan reservados.

El acceso se concede de manera limitada y revocable, con el único propósito de la evaluación académica en el marco del Global South AI Safety Hackathon 2026. No se transfiere ningún derecho de propiedad ni licencia de uso más allá de ese propósito.

Queda prohibida, sin autorización previa y por escrito de los titulares, la reproducción total o parcial, la distribución, la comunicación pública, la modificación, la creación de obras derivadas, el uso comercial y la incorporación del contenido, en todo o en parte, en otros sistemas, productos o servicios.

El acceso a este material implica el compromiso de mantener su confidencialidad y de no divulgarlo a terceros. El uso no autorizado podrá dar lugar a las acciones legales que correspondan conforme a la normativa aplicable de derecho de autor y propiedad intelectual.
