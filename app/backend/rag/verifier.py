"""
Guardrail determinista: validación de citas contra el índice del corpus.

Toda referencia normativa que el LLM mencione (controles ISO, funciones NIST)
debe existir realmente en el corpus o en las fuentes que se le pasaron. Si
inventa una cita ("ISO 42001 A.99" inexistente), se detecta y se marca. Barato,
determinista, y la segunda capa de defensa anti-alucinación.
"""

from __future__ import annotations

import re
from functools import lru_cache

from engine import load_data

_PATRONES = [
    re.compile(r"\bA\.\d+(?:\.\d+)?\b"),              # controles ISO (A.3.2, A.9.2, A.10.3)
    re.compile(r"NIST\s+AI\s+RMF(?:\s+\d+\.\d+)?", re.IGNORECASE),
    re.compile(r"\b(GOVERN|MAP|MEASURE|MANAGE)\b"),   # funciones NIST
]


@lru_cache(maxsize=1)
def _indice_referencias() -> set[str]:
    """Conjunto normalizado de todas las referencias válidas del corpus + controls.json."""
    refs: set[str] = set()
    data = load_data()
    for c in data["corpus"]:
        blob = " ".join(str(c.get(k, "")) for k in ("referencia", "referencia_legal", "id_control"))
        for pat in _PATRONES:
            for m in pat.findall(blob):
                refs.add(_norm(m))
    # incluir también los IDs de control de controls.json (ej. A.5.1, A.5.3, A.8.5, A.10.3)
    for ctrl in data["controls"].get("iso_controls", []):
        refs.add(_norm(ctrl.get("id", "")))
    return refs


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def encontrar_citas(texto: str) -> list[str]:
    citas = []
    for pat in _PATRONES:
        citas.extend(pat.findall(texto))
    return citas


def validar(texto: str, fuentes: list[dict] | None = None) -> dict:
    """
    Verifica que cada cita del texto exista en el corpus (y opcionalmente en las
    fuentes recuperadas). Devuelve {'validas': [...], 'invalidas': [...], 'ok': bool}.
    """
    indice = _indice_referencias()
    if fuentes:
        for f in fuentes:
            blob = " ".join(str(f.get(k, "")) for k in ("referencia", "referencia_legal", "id_control"))
            for pat in _PATRONES:
                for m in pat.findall(blob):
                    indice = indice | {_norm(m)}

    validas, invalidas = [], []
    for cita in encontrar_citas(texto):
        (validas if _norm(cita) in indice else invalidas).append(cita)
    return {
        "validas": sorted(set(validas)),
        "invalidas": sorted(set(invalidas)),
        "ok": len(invalidas) == 0,
    }
