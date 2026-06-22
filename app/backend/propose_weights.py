"""
Propuesta de pesos por eje — ejecución de UNA SOLA VEZ (fase de diseño).

Para cada pregunta del árbol (base + subpreguntas que puntúan), usa el RAG
(retrieval normativo + LLM OpenCode) para proponer un peso 0..1 en cada eje
(ético, iso, nist) con su justificación, fundamentado en NIST / ISO / principios.
El resultado se escribe en data/pesos_propuestos.json para que el equipo lo
REVISE y luego CONGELE los valores dentro de questions.json (campo "pesos").

Tras congelarlos, el runtime es 100% determinista: mismas respuestas → mismas
coordenadas para todas las PYMES.

Salta las preguntas tipo "texto" (no puntúan, no necesitan pesos).

Uso (requiere API key de OpenCode, ya configurada en auth.json o OPENCODE_API_KEY):
    .venv/bin/python propose_weights.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from rag import llm_client
from rag.retriever import retrieve
from engine import load_data

SALIDA = Path(__file__).parent / "data" / "pesos_propuestos.json"

# Modelo para tareas JSON (no-razonamiento): más rápido y limpio que glm-5.2 para
# salidas estructuradas. Pesos ya congelados con glm-5.2 — este modelo es para
# re-corridas futuras si se añaden preguntas.
MODELO_JSON = os.getenv("OPENCODE_MODEL_JSON", "deepseek-v4-flash")

SYSTEM = (
    "Eres un experto en gobernanza de IA (NIST AI RMF, ISO 42001) y en ética de IA "
    "(principios UNESCO/OCDE: beneficencia, no maleficencia, autonomía, justicia, "
    "explicabilidad). Para cada pregunta de autodiagnóstico debes estimar qué tan "
    "informativa es para medir cada uno de los tres ejes: ÉTICO, ISO y NIST. "
    "Asignas un peso de 0.0 a 1.0 por eje (0 = no informa ese eje; 1 = lo informa "
    "directamente y de forma central). Te basas SOLO en los fragmentos normativos "
    "provistos y en el mapeo declarado. Respondes en JSON estricto. "
    "NO incluyas razonamiento previo: devuelve ÚNICAMENTE el objeto JSON."
)

PROMPT = """Pregunta: "{texto}"
Mapeo declarado: NIST={nist} · ISO={iso} · principios={principio}

Fragmentos normativos relevantes:
{contexto}

Responde ÚNICAMENTE con este objeto JSON (sin markdown, sin texto antes ni después):
{{"etico": <0.0..1.0>, "iso": <0.0..1.0>, "nist": <0.0..1.0>, "justificacion": "<una frase citando la fuente>"}}"""


def _extraer_json(texto: str) -> dict:
    """Extrae el objeto JSON de la respuesta. El modelo puede emitir razonamiento
    antes (con llaves { dentro de la prosa); usa escaneo de llaves balanceadas
    y se queda con el último bloque que parsea y contiene las claves esperadas."""
    # escanear bloques {...} balanceados
    bloques = []
    profundidad = 0
    inicio = -1
    dentro_cadena = False
    escape = False
    for i, ch in enumerate(texto):
        if dentro_cadena:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                dentro_cadena = False
            continue
        if ch == '"':
            dentro_cadena = True
        elif ch == "{":
            if profundidad == 0:
                inicio = i
            profundidad += 1
        elif ch == "}":
            profundidad -= 1
            if profundidad == 0 and inicio >= 0:
                bloques.append(texto[inicio:i + 1])
                inicio = -1
    # probar de último a primero (la respuesta final suele ser el último bloque)
    for cand in reversed(bloques):
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict) and any(k in obj for k in ("etico", "iso", "nist")):
                return obj
        except Exception:
            continue
    raise ValueError(f"no se encontró JSON válido; raw={texto[:200]!r}")


def _iter_preguntas(preguntas: list[dict]):
    """Itera base + subpreguntas (hasta 2 niveles). Salta tipo texto."""
    for p in preguntas:
        if p.get("tipo") != "texto":
            yield p
        for sub in p.get("subpreguntas", []):
            if sub.get("tipo") != "texto":
                yield sub
            for sub2 in sub.get("subpreguntas", []):
                if sub2.get("tipo") != "texto":
                    yield sub2


def main() -> int:
    if not llm_client.disponible():
        print("Sin API key de OpenCode. Configúrala con OPENCODE_API_KEY o en auth.json de opencode.")
        return 1

    data = load_data()
    resultado = {}
    total = 0

    for q in _iter_preguntas(data["questions"]["preguntas"]):
        mapeo = q.get("mapeo", {})
        rec = retrieve(q["texto"],
                       filtro={"iso": mapeo.get("iso", []), "nist": mapeo.get("nist", [])},
                       top_k=5)
        contexto = "\n".join(f"- [{c['referencia_legal']}] {c['texto'][:300]}" for c in rec["chunks"])
        prompt = PROMPT.format(texto=q["texto"], nist=mapeo.get("nist", []),
                               iso=mapeo.get("iso", []), principio=mapeo.get("principio", []),
                               contexto=contexto or "(sin fragmentos)")
        try:
            texto_resp = llm_client.chat([{"role": "user", "content": prompt}],
                                         system=SYSTEM, max_tokens=1200, temperature=0.1,
                                         model=MODELO_JSON)
            pesos = _extraer_json(texto_resp)
        except Exception as e:
            pesos = {"error": str(e), "raw": texto_resp[:200] if 'texto_resp' in dir() else None}
        resultado[q["id"]] = pesos
        total += 1
        print(f"  {q['id']}: etico={pesos.get('etico')} iso={pesos.get('iso')} nist={pesos.get('nist')}")

    SALIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nPropuestos pesos para {total} preguntas en {SALIDA}.")
    print("REVISE los pesos y luego cópialos al campo 'pesos' de cada pregunta en questions.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
