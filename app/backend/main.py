"""
API del SaaS de autodiagnóstico de IA responsable.

Endpoints:
  GET  /api/health      estado y capacidades activas (keys presentes)
  GET  /api/questions   árbol de preguntas (bifurcación + preguntas)
  POST /api/diagnose    Capa 1 (diagnóstico) + Capa 2 (recomendaciones)
  POST /api/policy      Capa 3: genera política con RAG (retrieve+generate+verify)

Ejecutar: .venv/bin/uvicorn main:app --reload
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from engine import diagnosticar, load_data, recomendar  # noqa: E402
from artifacts import (  # noqa: E402
    generar_plan_accionable, generar_constancia,
    constancia_a_markdown, plan_a_markdown,
)
from informe_pdf import generar_informe_pdf  # noqa: E402
from rag.generator import generar_politica  # noqa: E402
from rag import llm_client  # noqa: E402
from rag.faithfulness import verificar as verificar_faithfulness  # noqa: E402
from rag.retriever import retrieve  # noqa: E402
from rag.verifier import validar  # noqa: E402
from evidence_analyzer import analizar_evidencia  # noqa: E402
from fastapi.responses import Response  # noqa: E402

app = FastAPI(title="Playbook IA Responsable — API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DiagnoseIn(BaseModel):
    bifurcacion: str
    respuestas: dict[str, str | list[str] | int]  # opción única, múltiple selección, o número
    evidencias: list[str] = []
    pais: str | None = "CO"


class PolicyIn(BaseModel):
    bifurcacion: str
    sector: str | None = None
    pais: str | None = "CO"
    brechas: list[dict]
    faithfulness: bool = True  # activa el verificador LLM-as-judge (3ª capa anti-alucinación)


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "llm": llm_client.disponible(),
        "voyage": bool(os.getenv("VOYAGE_API_KEY")),
        "modelo": os.getenv("OPENCODE_MODEL", "glm-5.2"),
        "modo": "completo" if llm_client.disponible() else "degradado (sin LLM)",
    }


@app.get("/api/questions")
def questions():
    return load_data()["questions"]


@app.post("/api/diagnose")
def diagnose(body: DiagnoseIn):
    diag = diagnosticar(body.bifurcacion, body.respuestas, body.evidencias)
    recs = recomendar(diag["gap_register"], pais=body.pais)
    return {"capa1": diag, "capa2": recs}


class ArtifactsIn(BaseModel):
    bifurcacion: str
    respuestas: dict[str, str | list[str] | int]
    evidencias: list[str] = []
    pais: str | None = "CO"
    sector: str | None = None
    generar_politica: bool = False  # si True, también genera política con RAG
    faithfulness: bool = False


@app.post("/api/artifacts")
def artifacts(body: ArtifactsIn):
    """Devuelve plan accionable (3.5) + constancia verificable (3.6).
    Opcionalmente genera política (3.1) si generar_politica=True."""
    diag = diagnosticar(body.bifurcacion, body.respuestas, body.evidencias)
    recs = recomendar(diag["gap_register"], pais=body.pais)
    plan = generar_plan_accionable(recs)

    politica = None
    if body.generar_politica and recs:
        iso = [r["id_control"] for r in recs if r.get("id_control")]
        nist = [r["nist"] for r in recs if r.get("nist")]
        query = "política de IA responsable: " + ", ".join(
            r.get("brecha", r.get("nombre", "")) for r in recs)
        rec_ret = retrieve(query, filtro={"iso": iso, "nist": nist}, top_k=6, pais=body.pais)
        if not rec_ret["abstain"]:
            perfiles = {
                "1": "Desarrolla productos/servicios con IA para terceros",
                "2": "Automatiza procesos internos con IA",
                "3": "Desarrolla productos con IA y automatiza procesos internos",
            }
            ctx = {"descripcion": perfiles.get(body.bifurcacion, ""), "sector": body.sector}
            politica = generar_politica(ctx, recs, rec_ret["chunks"])

    org = {"pais": body.pais, "sector": body.sector}
    constancia = generar_constancia(diag, recs, politica, org)
    return {
        "plan": plan,
        "plan_markdown": plan_a_markdown(plan),
        "constancia": constancia,
        "constancia_markdown": constancia_a_markdown(constancia),
    }


class InformeIn(BaseModel):
    bifurcacion: str
    respuestas: dict[str, str | list[str] | int]
    evidencias: list[str] = []
    pais: str | None = "CO"
    sector: str | None = None
    politica: dict | None = None       # política ya generada (si existe), para incluir en el PDF
    faithfulness: dict | None = None   # faithfulness ya calculado (si existe)


@app.post("/api/informe")
def informe(body: InformeIn):
    """Genera el informe PDF completo descargable."""
    diag = diagnosticar(body.bifurcacion, body.respuestas, body.evidencias)
    recs = recomendar(diag["gap_register"], pais=body.pais)
    org = {"pais": body.pais, "sector": body.sector,
           "perfil": diag["perfil"]["descripcion"]}
    pdf_bytes = generar_informe_pdf(
        diag, recs,
        politica=body.politica,
        organizacion=org,
        faithfulness=body.faithfulness,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="informe_autodiagnostico_IA.pdf"'},
    )


@app.post("/api/policy")
def policy(body: PolicyIn):
    # Construye consulta + filtro estructurado a partir de las brechas.
    iso = [b["id_control"] for b in body.brechas if b.get("id_control")]
    nist = [b["nist"] for b in body.brechas if b.get("nist")]
    query = "política de IA responsable: " + ", ".join(
        b.get("brecha", b.get("nombre", "")) for b in body.brechas
    )
    rec = retrieve(query, filtro={"iso": iso, "nist": nist}, top_k=6, pais=body.pais)

    if rec["abstain"]:
        return {"abstain": True, "mensaje": "Sin fundamento normativo suficiente para generar."}

    perfiles = {
        "1": "Desarrolla productos/servicios con IA para terceros",
        "2": "Automatiza procesos internos con IA",
        "3": "Desarrolla productos con IA y automatiza procesos internos",
    }
    contexto = {"descripcion": perfiles.get(body.bifurcacion, ""), "sector": body.sector}

    pol = generar_politica(contexto, body.brechas, rec["chunks"])
    verificacion = validar(pol["texto"], rec["chunks"])
    faith = verificar_faithfulness(pol["texto"], rec["chunks"]) if body.faithfulness else None

    return {
        "abstain": False,
        "politica": pol,
        "fuentes": [
            {"fuente": c["fuente"], "referencia": c["referencia"], "score": c.get("score")}
            for c in rec["chunks"]
        ],
        "verificacion": verificacion,
        "faithfulness": faith,
    }


@app.post("/api/analyze-evidence")
async def analyze_evidence(
    pregunta_id: str = File(...),
    archivo: UploadFile = File(...),
):
    """Extrae texto de un documento y calcula cobertura heurística de palabras clave
    respecto a la pregunta indicada. Escalable a verificación semántica con LLM."""
    contenido = await archivo.read()
    return analizar_evidencia(contenido, archivo.filename, pregunta_id)
