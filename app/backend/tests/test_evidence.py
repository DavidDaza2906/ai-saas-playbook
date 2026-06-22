"""Tests del analizador de evidencias (heurístico, sin red externa).

Correr: .venv/bin/pytest tests/test_evidence.py -v
"""

from __future__ import annotations

import io

import pytest

from evidence_analyzer import (
    analizar_evidencia,
    extraer_texto,
    palabras_clave_de_pregunta,
    score_cobertura,
)


def test_extraer_texto_docx():
    """Extrae texto de un documento DOCX generado en memoria."""
    try:
        from docx import Document
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"python-docx no disponible: {exc}")

    doc = Document()
    doc.add_paragraph("Documento de gobernanza de IA. Comité de ética.")
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    texto, err = extraer_texto(buffer.getvalue(), "gobernanza.docx")
    assert err is None
    assert "comité" in texto.lower()


def test_extraer_texto_pdf():
    """Extrae texto de un PDF generado en memoria."""
    try:
        from reportlab.pdfgen import canvas
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"reportlab no disponible: {exc}")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(72, 700, "Política de IA. Supervisión humana y riesgos.")
    c.save()
    buffer.seek(0)
    texto, err = extraer_texto(buffer.getvalue(), "politica.pdf")
    assert err is None
    assert "supervisión humana" in texto.lower()


def test_score_cobertura_basico():
    """El score es el cociente de palabras clave encontradas."""
    texto = "Tenemos un comité de ética y documentamos riesgos de privacidad"
    palabras = {"comité", "ética", "riesgos", "privacidad", "supervisión"}
    score, encontradas = score_cobertura(texto, palabras)
    assert score == len(encontradas) / len(palabras)
    assert "ética" in encontradas or "comité" in encontradas


def test_score_cobertura_texto_vacio():
    """Texto vacío retorna score cero sin error."""
    score, encontradas = score_cobertura("", {"comité", "ética"})
    assert score == 0
    assert encontradas == []


def test_analizar_evidencia_formato_desconocido():
    """Un archivo con extensión desconocida retorna error educativo."""
    body = analizar_evidencia(b"contenido", "archivo.xyz", "q1")
    assert "error" in body
    assert body["escalable_a_llm"] is True


def test_analizar_evidencia_texto_plano():
    """Un archivo de texto plano se analiza directamente."""
    body = analizar_evidencia(
        b"Documento de gobernanza. Comite de etica. Riesgos documentados.",
        "evidencia.txt",
        "q1",
    )
    assert body["pregunta_id"] == "q1"
    assert body["error"] is None
    assert body["caracteres"] > 0
    assert body["score"] >= 0
