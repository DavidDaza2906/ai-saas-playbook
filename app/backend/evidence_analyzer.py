"""
Análisis heurístico de evidencias documentales adjuntas.

Capa opcional de verificación: extrae texto de PDF/DOCX/TXT y calcula una
cobertura de palabras clave asociadas a la pregunta y su mapeo normativo.
Diseñado para ser escalable a verificación semántica con LLM (Opción 3).
"""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any

from engine import load_data

_STOPWORDS = {
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por",
    "un", "para", "con", "no", "una", "su", "al", "lo", "más", "pero", "sus",
    "le", "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando", "muy",
    "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde",
    "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra", "otros",
    "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos", "qué",
    "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho",
    "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas",
    "algo", "nosotros", "mi", "mis", "tú", "te", "ti", "tu", "tus", "ellas",
    "nosotras", "vosotros", "vosotras", "os", "mío", "mía", "míos", "mías",
    "tuyo", "tuya", "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas",
    "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra",
    "vuestros", "vuestras", "esos", "esas", "estoy", "estás", "está",
    "estamos", "estáis", "están", "esté", "estés", "estemos", "estéis",
    "estén", "estaré", "estarás", "estará", "estaremos", "estaréis",
    "estarán", "ser", "soy", "eres", "es", "somos", "sois", "son", "sea",
    "seas", "seamos", "seáis", "sean", "era", "eras", "éramos", "erais",
    "eran", "fui", "fuiste", "fue", "fuimos", "fuisteis", "fueron", "haber",
    "he", "has", "ha", "hemos", "habéis", "han", "haya", "hayas", "hayamos",
    "hayáis", "hayan", "había", "habías", "habíamos", "habíais", "habían",
    "tener", "tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen",
    "tenga", "tengas", "tengamos", "tengáis", "tengan", "tenía", "tenías",
    "teníamos", "teníais", "tenían", "hacer", "hago", "haces", "hace",
    "hacemos", "hacéis", "hacen", "haga", "hagas", "hagamos", "hagáis",
    "hagan", "hacía", "hacías", "hacíamos", "hacíais", "hacían", "poder",
    "puedo", "puedes", "puede", "podemos", "podéis", "pueden", "pueda",
    "puedas", "podamos", "podáis", "puedan", "podía", "podías", "podíamos",
    "podíais", "podían", "ir", "voy", "vas", "va", "vamos", "vais", "van",
    "vaya", "vayas", "vayamos", "vayáis", "vayan", "iba", "ibas", "íbamos",
    "ibais", "iban", "ver", "veo", "ves", "ve", "vemos", "veis", "ven",
    "vea", "veas", "veamos", "veáis", "vean", "veía", "veías", "veíamos",
    "veíais", "veían", "dar", "doy", "das", "da", "damos", "dais", "dan",
    "dé", "des", "demos", "deis", "den", "decir", "digo", "dices", "dice",
    "decimos", "decís", "dicen", "diga", "digas", "digamos", "digáis",
    "digan", "decía", "decías", "decíamos", "decíais", "decían",
}


def _tokenizar(texto: str) -> set[str]:
    """Extrae palabras significativas en minúsculas, sin stopwords ni números sueltos."""
    tokens = re.findall(r"[a-záéíóúñ]+", texto.lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 2}


def _extraer_texto_pdf(archivo: bytes) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=archivo, filetype="pdf")
        partes = []
        for page in doc:
            partes.append(page.get_text())
        return "\n".join(partes)
    except Exception as e:
        return f"[Error extrayendo PDF: {e}]"


def _extraer_texto_docx(archivo: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(archivo))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return f"[Error extrayendo DOCX: {e}]"


def extraer_texto(archivo: bytes, filename: str) -> tuple[str, str | None]:
    """Extrae texto plano de PDF, DOCX o TXT. Retorna (texto, error)."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        texto = _extraer_texto_pdf(archivo)
    elif ext == ".docx":
        texto = _extraer_texto_docx(archivo)
    elif ext == ".txt":
        texto = archivo.decode("utf-8", errors="ignore")
    else:
        texto = "[Formato no soportado]"
    if texto.startswith("[Error") or texto.startswith("[Formato"):
        return "", texto
    return texto, None


def score_cobertura(texto: str, palabras_clave: set[str]) -> tuple[float, list[str]]:
    """Calcula score de cobertura y retorna (score, coincidencias)."""
    if not palabras_clave:
        return 0.0, []
    tokens_doc = _tokenizar(texto)
    coincidencias = sorted(palabras_clave & tokens_doc)
    return round(len(coincidencias) / len(palabras_clave), 3), coincidencias


def _cargar_datos() -> dict[str, Any]:
    return load_data()


def palabras_clave_de_pregunta(pregunta: dict, data: dict) -> set[str]:
    """Construye un conjunto de palabras clave a partir de la pregunta y su mapeo normativo."""
    texto = " ".join([
        pregunta.get("texto", ""),
        pregunta.get("contexto_pyme", ""),
    ])
    palabras = _tokenizar(texto)

    mapeo = pregunta.get("mapeo", {})

    iso_ids = mapeo.get("iso", []) or []
    iso_index = {c["id"]: c for c in data["controls"].get("iso_controls", [])}
    for cid in iso_ids:
        ctrl = iso_index.get(cid, {})
        texto_iso = " ".join([
            ctrl.get("id", ""),
            ctrl.get("nombre", ""),
            ctrl.get("descripcion", ""),
        ])
        palabras |= _tokenizar(texto_iso)

    nist_ids = mapeo.get("nist", []) or []
    nist_index = {f["id"]: f for f in data["controls"].get("nist_functions", [])}
    for fid in nist_ids:
        func = nist_index.get(fid, {})
        texto_nist = " ".join([
            func.get("id", ""),
            func.get("nombre", ""),
            func.get("descripcion", ""),
        ])
        palabras |= _tokenizar(texto_nist)

    principios = mapeo.get("principio", []) or []
    for p in principios:
        palabras |= _tokenizar(p)

    return palabras


def analizar_evidencia(archivo: bytes, filename: str, pregunta_id: str) -> dict[str, Any]:
    """
    Analiza un documento adjunto y devuelve un score heurístico de cobertura
    respecto a la pregunta indicada.

    Salida:
      {
        "pregunta_id": str,
        "filename": str,
        "caracteres": int,
        "palabras_clave": int,
        "encontradas": int,
        "score": float,  # 0.0 - 1.0
        "coincidencias": [str],
        "escalable_a_llm": True,  # flag para futura Opción 3
      }
    """
    data = _cargar_datos()

    # Buscar la pregunta (base o subpregunta)
    pregunta = None
    for p in data["questions"].get("preguntas", []):
        if p["id"] == pregunta_id:
            pregunta = p
            break
        for sub in p.get("subpreguntas", []):
            if sub["id"] == pregunta_id:
                pregunta = sub
                break
            for sub2 in sub.get("subpreguntas", []):
                if sub2["id"] == pregunta_id:
                    pregunta = sub2
                    break
        if pregunta:
            break

    if pregunta is None:
        return {
            "pregunta_id": pregunta_id,
            "filename": filename,
            "error": f"Pregunta {pregunta_id} no encontrada",
        }

    texto_doc, error = extraer_texto(archivo, filename)
    if error:
        return {
            "pregunta_id": pregunta_id,
            "filename": filename,
            "caracteres": 0,
            "palabras_clave": 0,
            "encontradas": 0,
            "score": 0.0,
            "coincidencias": [],
            "escalable_a_llm": True,
            "error": error,
        }

    palabras_clave = palabras_clave_de_pregunta(pregunta, data)
    score, coincidencias = score_cobertura(texto_doc, palabras_clave)

    return {
        "pregunta_id": pregunta_id,
        "filename": filename,
        "caracteres": len(texto_doc),
        "palabras_clave": len(palabras_clave),
        "encontradas": len(coincidencias),
        "score": score,
        "coincidencias": coincidencias,
        "escalable_a_llm": True,
        "error": None,
    }
