"""Tests end-to-end de la API FastAPI (TestClient, sin red externa).

Correr: .venv/bin/pytest tests/test_api.py -v

Estos tests usan el TestClient de FastAPI (no levanta servidor real).
No requieren keys de OpenCode ni Voyage — el motor determinista y el
fallback de plantilla funcionan sin red.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_reporta_modo():
    """/health devuelve ok=True + modo (degradado o completo)."""
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "modo" in body
    # modo debe ser "completo" o "degradado (sin LLM)"
    assert "completo" in body["modo"] or "degradado" in body["modo"]


def test_questions_arbol_completo():
    """/questions devuelve bifurcación + 15 preguntas base + subpreguntas."""
    r = client.get("/api/questions")
    assert r.status_code == 200
    q = r.json()
    assert "bifurcacion" in q
    assert "preguntas" in q
    assert len(q["preguntas"]) == 15, f"esperaba 15 base, got {len(q['preguntas'])}"
    # verificar que hay subpreguntas
    total_subs = sum(len(p.get("subpreguntas", [])) for p in q["preguntas"])
    assert total_subs == 19, f"esperaba 19 subpreguntas, got {total_subs}"


def test_diagnose_caso_poc():
    """/diagnose con caso POC devuelve vector + gaps + recomendaciones."""
    caso = {
        "bifurcacion": "3",
        "respuestas": {
            "q1": "parcial", "q2": ["c"], "q2a": "parcial",
            "q3": 3, "q3b": "algunos", "q4": ["medio", "alto", "bajo"],
            "q5": "2", "q5a": "parcial", "q5b": "no",
            "q6": "si", "q6a": "no", "q6b": "no", "q6c": "no",
            "q7": ["c"], "q7a": "nadie", "q7b": "nunca",
            "q8a": "2", "q8a_just": "temor",
            "q8b": ["d"], "q8b_herr": "no",
            "q9b": "si", "q9a": "no", "q9b_doc": "no",
            "q10b": "2", "q10a": "no", "q10b_mon": "nadie",
            "q11": "si", "q11a": "no", "q11b": "no",
            "q12": "si", "q12a": "no", "q12b": "no",
            "q13": "3", "q13_just": "x",
        },
        "evidencias": ["q1"],
        "pais": "CO",
    }
    r = client.post("/api/diagnose", json=caso)
    assert r.status_code == 200
    body = r.json()
    assert "capa1" in body
    assert "capa2" in body
    # vector presente
    v = body["capa1"]["diagnostico_vector"]
    assert "x_etico" in v and "y_iso" in v and "z_nist" in v
    # gaps presentes y no vacíos
    gaps = body["capa1"]["gap_register"]
    assert len(gaps) > 0, "debe haber brechas"
    # recomendaciones presentes
    recs = body["capa2"]
    assert len(recs) > 0, "debe haber recomendaciones"
    # recomendaciones ordenadas por prioridad
    prioridades = [r["prioridad"] for r in recs]
    assert prioridades == sorted(prioridades, reverse=True)


def test_analyze_evidence_pdf_texto():
    """/analyze-evidence acepta un PDF de texto y devuelve score de cobertura."""
    import io
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(72, 700, "Tenemos un comité de ética de IA y documentamos riesgos.")
    c.save()
    buffer.seek(0)

    r = client.post(
        "/api/analyze-evidence",
        data={"pregunta_id": "q1"},
        files={"archivo": ("etica.pdf", buffer, "application/pdf")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["pregunta_id"] == "q1"
    assert body["caracteres"] > 0
    assert body["palabras_clave"] > 0
    assert 0 <= body["score"] <= 1
    assert body["escalable_a_llm"] is True


def test_artifacts_plan_y_constancia():
    """/artifacts devuelve plan accionable + constancia verificable (sin política)."""
    caso = {
        "bifurcacion": "3",
        "respuestas": {
            "q1": "parcial", "q2": ["c"], "q2a": "parcial",
            "q3": 3, "q3b": "algunos", "q4": ["medio", "alto", "bajo"],
            "q5": "2", "q5a": "parcial", "q5b": "no",
            "q6": "si", "q6a": "no", "q6b": "no", "q6c": "no",
            "q7": ["c"], "q8a": "2", "q8b": ["d"], "q8b_herr": "no",
            "q9b": "si", "q9a": "no", "q9b_doc": "no",
            "q10b": "2", "q10a": "no", "q11": "si", "q11a": "no", "q11b": "no",
            "q12": "si", "q12a": "no", "q12b": "no",
            "q13": "3", "q13_just": "x",
        },
        "evidencias": ["q1"],
        "pais": "CO",
        "sector": "Comercio",
        "generar_politica": False,
    }
    r = client.post("/api/artifacts", json=caso)
    assert r.status_code == 200
    body = r.json()
    # plan
    assert "plan" in body
    assert body["plan"]["resumen"]["n_tareas"] > 0
    assert "0-30" in body["plan"]["fases"]
    assert len(body["plan_markdown"]) > 100
    # constancia
    assert "constancia" in body
    c = body["constancia"]
    assert c["titulo"] == "Constancia de Autodiagnóstico de Gobernanza de IA"
    assert c["organizacion"]["pais"] == "CO"
    assert c["organizacion"]["sector"] == "Comercio"
    assert c["que_se_encontro"]["n_brechas_total"] > 0
    assert "vector_diagnostico" in c["que_se_encontro"]
    assert len(body["constancia_markdown"]) > 200
    # sin política
    assert c["que_se_genero"]["politica_generada"] is False


def test_artifacts_plan_tienen_tareas_asignables():
    """Cada tarea del plan tiene acción, responsable, fase y criterio de cierre."""
    from artifacts import generar_plan_accionable
    recs = [
        {"id_control": "A.9.2", "brecha": "Sin supervisión", "recomendacion": "Implementar",
         "rol": "Responsable IA", "fase": "0-30", "criterio_cierre": "Flujo documentado",
         "prioridad": 3.0, "esfuerzo": "bajo", "severidad": "alta"},
        {"id_control": "A.6.2", "brecha": "Datos sin gobernanza", "recomendacion": "Documentar",
         "rol": "Responsable datos", "fase": "30-90", "criterio_cierre": "Registro",
         "prioridad": 1.5, "esfuerzo": "medio", "severidad": "alta"},
    ]
    plan = generar_plan_accionable(recs)
    for fase, tareas in plan["fases"].items():
        for t in tareas:
            assert t["accion"], "tarea sin acción"
            assert t["responsable"], "tarea sin responsable"
            assert t["fase"] == fase
            assert t["criterio_cierre"], "tarea sin criterio de cierre"
    assert plan["resumen"]["n_tareas"] == 2
    assert plan["resumen"]["n_quick_wins_0_30"] == 1
