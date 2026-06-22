# Backend — Playbook IA Responsable

API del SaaS de autodiagnóstico. Núcleo determinista (Capa 1 + 2) + RAG normativo (Capa 3).

## Arquitectura

- `engine.py` — diagnóstico (Capa 1) y recomendaciones (Capa 2). Sin LLM, reproducible.
- `artifacts.py` — plan accionable (3.5) + constancia verificable (3.6).
- `informe_pdf.py` — generador de informe PDF (WeasyPrint).
- `rag/llm_client.py` — cliente de la API de OpenCode Go (glm-5.2).
- `rag/retriever.py` — retrieval híbrido: estructurado + BM25 + denso (Voyage) + RRF + rerank + umbral.
- `rag/generator.py` — Capa 3: política con LLM (glm-5.2) + prompt grounded-only.
- `rag/verifier.py` — 2ª capa anti-alucinación: validación de citas contra el índice.
- `rag/faithfulness.py` — 3ª capa anti-alucinación: verificador LLM-as-judge.
- `main.py` — API FastAPI.
- `data/` — árbol de preguntas, controles NIST/ISO, recomendaciones, corpus normativo, golden set.

## Modo degradado (sin keys)

Todo corre sin claves: retrieval estructurado + BM25, y política por plantilla.
- Con `OPENCODE_API_KEY` (o auth.json de opencode): política con LLM glm-5.2.
- Con `VOYAGE_API_KEY`: retrieval denso + rerank.

## Puesta en marcha

```bash
cd app/backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install weasyprint   # para informe PDF
cp .env.example .env                         # y completar VOYAGE_API_KEY (opcional)
.venv/bin/uvicorn main:app --reload          # http://127.0.0.1:8000
```

## Pruebas

```bash
.venv/bin/python poc.py                      # caso POC: Capa 1 + 2
.venv/bin/python validate_questions.py       # validar el árbol de preguntas
.venv/bin/python -m pytest tests/ -v         # 360 tests
.venv/bin/python eval_harness.py --con-faithfulness --report  # métricas RAGAS
```

## Endpoints

| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado y capacidades activas |
| GET | `/api/questions` | Árbol de preguntas (15 base + 19 subpreguntas) |
| POST | `/api/diagnose` | Diagnóstico (Capa 1) + recomendaciones (Capa 2) |
| POST | `/api/policy` | Política con RAG + faithfulness (Capa 3) |
| POST | `/api/artifacts` | Plan accionable + constancia verificable |
| POST | `/api/informe` | Informe PDF descargable |
