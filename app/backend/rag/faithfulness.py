"""
Verificador de faithfulness (LLM-as-judge) — 3ª capa anti-alucinación.

Comprueba que cada afirmación de la política generada está respaldada (entailed)
por las fuentes normativas recuperadas. Es la métrica de faithfulness de RAGAS
aplicada en línea, y la salvaguarda de seguridad de IA más diferenciadora del
proyecto (ver RAG.md §5 y §9).

Flujo:
  1. El LLM recibe la política + las fuentes.
  2. Identifica cada afirmación atómica en la política.
  3. Para cada una, verdict: faithful | unfaithful | partial, con la fuente citada.
  4. Agrega: score = faithful / total, lista de no respaldadas.

Una sola llamada LLM por política (eficiente). Usa el modelo JSON
(deepseek-v4-flash) por velocidad; si no hay key, degrada a heurística
(citas válidas en el índice → faithful asumido, marcado como modo: heuristica).
"""

from __future__ import annotations

import json
import os

from rag import llm_client
from rag.verifier import validar

SYSTEM = (
    "Eres un verificador de faithfulness (groundedness) para un sistema RAG de "
    "gobernanza de IA. Dada una política generada y las fuentes normativas "
    "recuperadas, identificas cada afirmación atómica de la política y verificas "
    "si está respaldada por esas fuentes. Criterios: "
    "(a) 'faithful' = el contenido sustantivo de la afirmación está entailed en "
    "alguna de las fuentes proporcionadas (aunque la política la parafrasee); "
    "(b) 'unfaithful' = la afirmación introduce obligaciones, artículos, leyes o "
    "detalles que NO están en ninguna de las fuentes proporcionadas (inventados); "
    "(c) 'partial' = parte de la afirmación está respaldada y parte no. "
    "Si la política cita una fuente que no está en la lista proporcionada, es "
    "'unfaithful'. Una paráfrasis fiel de una fuente es 'faithful'. "
    "IMPORTANTE: no incluyas razonamiento previo ni análisis visible. Devuelves "
    "ÚNICAMENTE el objeto JSON final, sin texto antes ni después, sin markdown."
)

PROMPT = """Fuentes normativas disponibles:
{fuentes}

Política generada a verificar:
---
{politica}
---

Identifica cada afirmación atómica en la política (una por idea sustantiva, no
una por frase). Para cada una, devuelve su veredicto.

Responde ÚNICAMENTE con este JSON (sin markdown, sin texto antes/después):
{{"claims": [
  {{"afirmacion": "<texto de la afirmación>", "veredicto": "faithful|unfaithful|partial", "fuente_citada": "<referencia_legal o null>", "explicacion": "<una frase>"}}
]}}"""


def _extraer_json(texto: str) -> dict:
    """Extrae el JSON de la respuesta. Maneja: texto solo-JSON, bloques markdown
    ```json ... ```, y razonamiento antes del JSON (escaneo de llaves balanceadas)."""
    import re
    # 1. intento: texto completo
    try:
        return json.loads(texto.strip())
    except Exception:
        pass
    # 2. intento: bloque markdown ```json ... ``` o ``` ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL)
    if m:
        try:
            obj = json.loads(m.group(1))
            if isinstance(obj, dict) and "claims" in obj:
                return obj
        except Exception:
            pass
    # 3. intento: escaneo de llaves balanceadas (cualquier bloque {...})
    bloques = []
    prof = 0
    inicio = -1
    en_cadena = False
    escape = False
    for i, ch in enumerate(texto):
        if en_cadena:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                en_cadena = False
            continue
        if ch == '"':
            en_cadena = True
        elif ch == "{":
            if prof == 0:
                inicio = i
            prof += 1
        elif ch == "}":
            prof -= 1
            if prof == 0 and inicio >= 0:
                bloques.append(texto[inicio:i + 1])
                inicio = -1
    for cand in reversed(bloques):
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict) and "claims" in obj:
                return obj
        except Exception:
            continue
    raise ValueError(f"JSON de faithfulness no encontrado; raw={texto[:200]!r}")


def verificar(texto: str, fuentes: list[dict], model: str | None = None) -> dict:
    """Verifica faithfulness de `texto` contra `fuentes`.

    Devuelve:
      {modo, claims: [...], score, faithful, n_claims, n_faithful, n_unfaithful, n_partial, no_respaldadas: [...]}
    `model` opcional: si se pasa, usa ese modelo (ej. 'kimi-k2.6'); si no, el default
    (OPENCODE_MODEL_FAITHFULNESS o glm-5.2).
    """
    if not llm_client.disponible() or not texto or not fuentes:
        return _heuristica(texto, fuentes)

    fuentes_txt = "\n".join(
        f"- [{f.get('referencia_legal', f.get('referencia', ''))}] {f['texto'][:400]}"
        for f in fuentes
    )
    prompt = PROMPT.format(fuentes=fuentes_txt, politica=texto)
    # glm-5.2 es fiable para JSON estructurado (verificado con propose_weights.py);
    # deepseek-v4-flash devuelve respuestas vacías en esta tarea.
    modelo = model or os.getenv("OPENCODE_MODEL_FAITHFULNESS", "glm-5.2")

    try:
        resp = llm_client.chat([{"role": "user", "content": prompt}],
                               system=SYSTEM, max_tokens=8000, temperature=0.1,
                               model=modelo)
        data = _extraer_json(resp)
    except Exception as e:
        out = _heuristica(texto, fuentes)
        out["error"] = str(e)
        return out

    claims = data.get("claims", [])
    n = len(claims)
    n_f = sum(1 for c in claims if c.get("veredicto") == "faithful")
    n_u = sum(1 for c in claims if c.get("veredicto") == "unfaithful")
    n_p = sum(1 for c in claims if c.get("veredicto") == "partial")
    score = round(n_f / n, 3) if n else None
    no_resp = [c for c in claims if c.get("veredicto") in ("unfaithful", "partial")]

    return {
        "modo": "llm",
        "claims": claims,
        "n_claims": n,
        "n_faithful": n_f,
        "n_unfaithful": n_u,
        "n_partial": n_p,
        "score": score,
        "faithful": n_u == 0 and n_p == 0,
        "no_respaldadas": no_resp,
    }


def _heuristica(texto: str, fuentes: list[dict]) -> dict:
    """Fallback sin LLM: valida citas contra el índice (verificador determinista).
    No verifica entailment real — solo que las citas mencionadas existen."""
    ver = validar(texto, fuentes)
    return {
        "modo": "heuristica",
        "claims": [],
        "n_claims": 0,
        "n_faithful": None,
        "n_unfaithful": len(ver.get("invalidas", [])),
        "n_partial": 0,
        "score": None,
        "faithful": ver.get("ok", False),
        "no_respaldadas": [{"afirmacion": "(modo heuristica: solo valida citas contra índice)",
                            "veredicto": "unfaithful" if ver.get("invalidas") else "faithful",
                            "citas_invalidas": ver.get("invalidas", [])}],
        "citas_validas": ver.get("validas", []),
    }
