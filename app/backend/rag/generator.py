"""
Capa 3 — generación de artefactos con LLM fundamentada en fuentes.

Genera la política de IA a la medida usando la API de OpenCode (glm-5.2) con
retrieval normativo: cada afirmación debe amarrarse al fragmento que la sustenta
(materializa la "constancia verificable"). Las citas se validan contra el índice
del corpus con rag/verifier.py (guardrail determinista anti-alucinación).

Degrada con elegancia: sin API key produce una política a partir de plantilla
rellenada con las fuentes recuperadas, para que la demo nunca dependa de la red.
"""

from __future__ import annotations

import re

from rag import llm_client

SYSTEM = (
    "Eres un asistente experto en gobernanza de IA para PYMES. Redactas políticas "
    "claras y accionables, en español, adecuadas a una empresa pequeña sin equipo "
    "legal. Reglas estrictas: (1) básate ÚNICAMENTE en los documentos normativos "
    "proporcionados; (2) cita la fuente (referencia_legal) de cada obligación que "
    "menciones; (3) si algo no está en los documentos, NO lo inventes y dilo; "
    "(4) lenguaje sencillo, sin tecnicismos innecesarios; "
    "(5) NO incluyas razonamiento interno ni análisis previo: entrega DIRECTAMENTE "
    "la política final, empezando por el título."
)


def _limpiar_salida(texto: str) -> str:
    """Quita el preamble de razonamiento si el modelo lo emitió.
    Conserva desde el primer título de política encontrado; si no hay título claro,
    devuelve el texto tal cual (mejor no recortar a ciegas)."""
    # patrones de inicio de política real
    patrones = [
        r"(?m)^(?:#{1,6}\s*)?(?:POL[ÍI]TICA|Pol[íi]tica)\s+(?:de\s+)?[Uu]so\s+[Rr]esponsable",
        r"(?m)^(?:#{1,6}\s*)?POL[ÍI]TICA\s+DE\s+(?:USO\s+)??[Rr]ES",
        r"(?ms)^Aqu[íi]\s+tienes\s+la\s+Pol[íi]tica.*?\n+((?:#{1,6}\s*)?Pol[íi]tica)",
    ]
    for pat in patrones:
        m = re.search(pat, texto)
        if m:
            inicio = m.start()
            if inicio > 0 and len(texto) - inicio > 200:  # solo recorta si el preamble es largo
                return texto[inicio:]
            break
    return texto


def _prompt_usuario(contexto: dict, brechas: list[dict], fuentes: list[dict]) -> str:
    lineas = [
        f"Contexto de la organización: {contexto.get('descripcion', '')}.",
        f"Sector: {contexto.get('sector', 'no especificado')}.",
        "",
        "Brechas detectadas que la política debe atender:",
    ]
    for b in brechas:
        lineas.append(f"- {b.get('brecha', b.get('nombre'))} (control {b['id_control']}).")
    lineas += ["", "Documentos normativos disponibles (úsalos como fundamento):"]
    for f in fuentes:
        lineas.append(f"- [{f.get('referencia_legal', f.get('referencia',''))}] {f['texto'][:600]}")
    lineas += [
        "",
        "Redacta una POLÍTICA DE USO RESPONSABLE DE IA para esta organización. "
        "Estructura: 1) Objetivo y alcance, 2) Principios, 3) Responsabilidades, "
        "4) Reglas de uso y supervisión humana, 5) Datos personales, 6) Revisión. "
        "Cita la referencia_legal de la fuente que sustenta cada obligación.",
    ]
    return "\n".join(lineas)


def generar_politica(contexto: dict, brechas: list[dict], fuentes: list[dict],
                     model: str | None = None) -> dict:
    """Devuelve {'texto': str, 'citas': [...], 'modo': 'llm'|'plantilla'}.
    `model` opcional: si se pasa, usa ese modelo (ej. 'kimi-k2.6'); si no, el default (glm-5.2)."""
    if not llm_client.disponible() or not fuentes:
        return _fallback(contexto, brechas, fuentes)

    try:
        texto = llm_client.chat(
            [{"role": "user", "content": _prompt_usuario(contexto, brechas, fuentes)}],
            system=SYSTEM, max_tokens=8000, temperature=0.2, model=model,
        )
    except Exception as e:  # red caída, cuota, etc. -> demo sigue
        out = _fallback(contexto, brechas, fuentes)
        out["error"] = str(e)
        return out

    texto = _limpiar_salida(texto)

    # Citas: las que el modelo mencionó en su texto y que están en el índice
    # (el verificador las valida contra el corpus — guardrail determinista).
    citas = [{"fuente": f.get("referencia_legal", f.get("referencia"))}
             for f in fuentes if f.get("referencia_legal") and f["referencia_legal"] in texto]
    return {"texto": texto, "citas": citas, "modo": "llm"}


def _fallback(contexto: dict, brechas: list[dict], fuentes: list[dict]) -> dict:
    """Política a partir de plantilla + fuentes recuperadas (sin LLM)."""
    refs = "; ".join(sorted({f["referencia_legal"] for f in (fuentes or [])}))
    brechas_txt = "\n".join(f"  - {b.get('brecha', b.get('nombre'))}" for b in brechas)
    texto = f"""POLÍTICA DE USO RESPONSABLE DE INTELIGENCIA ARTIFICIAL

1. OBJETIVO Y ALCANCE
Esta política establece el compromiso de la organización ({contexto.get('descripcion','')})
con el uso responsable, ético y conforme a la ley de los sistemas de inteligencia artificial.

2. PRINCIPIOS
La organización adopta los 5 principios consolidados (UNESCO/OCDE): beneficencia,
no maleficencia, autonomía, justicia y explicabilidad.

3. RESPONSABILIDADES
Se designa un responsable de IA encargado de la supervisión del cumplimiento de esta
política (ISO 42001 A.3.2).

4. REGLAS DE USO Y SUPERVISIÓN HUMANA
Toda decisión de IA que afecte a personas será revisada por una persona antes de surtir
efecto (ISO 42001 A.9.2; Constitución art. 13 y art. 29).

5. DATOS PERSONALES
El tratamiento de datos personales requiere autorización previa, expresa e informada del
titular, conforme a la normativa aplicable (Ley 1581 de 2012 art. 9 en Colombia) y al
habeas data (Constitución art. 15).

6. REVISIÓN
Esta política se revisará periódicamente y ante cambios significativos en los sistemas de IA.

Brechas que esta política contribuye a cerrar:
{brechas_txt}

Fuentes normativas: {refs}
"""
    return {"texto": texto, "citas": [], "modo": "plantilla"}
