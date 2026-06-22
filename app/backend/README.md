# Backend — Playbook IA Responsable

API del SaaS de autodiagnóstico. Núcleo determinista (Capa 1 + 2) + RAG normativo (Capa 3).

## Arquitectura
- `data/` — núcleo determinista: árbol de preguntas, controles NIST/ISO, recomendaciones y corpus normativo (chunks con metadatos).
- `engine.py` — diagnóstico (Capa 1) y recomendaciones (Capa 2). Sin LLM, reproducible.
- `rag/retriever.py` — retrieval híbrido: estructurado por ID + denso (Voyage) + BM25 + RRF + rerank + umbral de abstención.
- `rag/generator.py` — Capa 3: política con Claude + citations nativas.
- `rag/verifier.py` — guardrail: validación de citas contra el índice.
- `main.py` — API FastAPI.

## Modo degradado (sin keys)
Todo corre sin claves: retrieval estructurado + BM25, y política por plantilla.
Con `ANTHROPIC_API_KEY` y `VOYAGE_API_KEY` sube a retrieval denso + Claude + citations.

## Puesta en marcha
```bash
cd app/backend
python3 -m venv .venv                 # ya creado
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env                  # y completar las keys (opcional)
.venv/bin/uvicorn main:app --reload   # http://127.0.0.1:8000
```

## Prueba rápida
```bash
.venv/bin/python poc.py               # recorre el caso POC por Capa 1 y 2
```

## Endpoints
- `GET /api/health` — capacidades activas.
- `GET /api/questions` — árbol de preguntas.
- `POST /api/diagnose` — `{bifurcacion, respuestas, evidencias}` → Capa 1 + 2.
- `POST /api/policy` — `{bifurcacion, sector, brechas}` → Capa 3 (RAG).
