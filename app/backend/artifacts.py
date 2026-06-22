"""
Artefactos de Capa 3 — 3.5 Plan accionable y 3.6 Constancia verificable.

Deterministas: se ensamblan con datos que ya existen en Capa 1 + Capa 2.
No usan LLM (la política 3.1 sí usa RAG; estos no).

3.5 Plan de implementación accionable: tareas asignables con responsable y
    fecha, derivadas de la secuenciación de la Capa 2.
3.6 Constancia verificable: registro con fecha y referencia de qué se evaluó,
    qué se encontró y qué se generó. Materializa el adjetivo "verificable" y
    funciona como activo comercial/regulatorio que la PYME puede presentar.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def generar_plan_accionable(recomendaciones: list[dict]) -> dict[str, Any]:
    """3.5 — Plan de implementación accionable.

    Toma las recomendaciones priorizadas de Capa 2 y las convierte en tareas
    asignables agrupadas por fase (0-30 días, 30-90 días, estructural).

    Devuelve: {fases: {fase: [tarea]}, resumen: {n_tareas, n_fases, ...}}
    Cada tarea: {control, brecha, accion, responsable, fase, criterio_cierre, prioridad}
    """
    fases: dict[str, list[dict]] = {"0-30": [], "30-90": [], "estructural": []}
    for rec in recomendaciones:
        fase = rec.get("fase", "30-90")
        if fase not in fases:
            fase = "30-90"
        tarea = {
            "control": rec.get("id_control"),
            "brecha": rec.get("brecha"),
            "accion": rec.get("recomendacion"),
            "responsable": rec.get("rol"),
            "fase": fase,
            "criterio_cierre": rec.get("criterio_cierre"),
            "prioridad": rec.get("prioridad"),
            "esfuerzo": rec.get("esfuerzo"),
            "severidad": rec.get("severidad"),
        }
        fases[fase].append(tarea)

    # ordenar tareas dentro de cada fase por prioridad desc
    for fase in fases:
        fases[fase].sort(key=lambda t: t.get("prioridad", 0), reverse=True)

    resumen = {
        "n_tareas": sum(len(ts) for ts in fases.values()),
        "n_quick_wins_0_30": len(fases["0-30"]),
        "n_mediano_plazo_30_90": len(fases["30-90"]),
        "n_estructural": len(fases["estructural"]),
    }
    return {"fases": fases, "resumen": resumen}


def generar_constancia(diagnostico: dict, recomendaciones: list[dict],
                       politica: dict | None = None,
                       organizacion: dict | None = None) -> dict[str, Any]:
    """3.6 — Constancia verificable.

    Registro con fecha y referencia de qué se evaluó, qué se encontró y qué se
    generó. Materializa el adjetivo "verificable" del sistema.

    Devuelve un dict con todos los campos del registro.
    """
    org = organizacion or {}
    v = diagnostico.get("diagnostico_vector", {})
    verif = diagnostico.get("verificabilidad", {})
    gaps = diagnostico.get("gap_register", [])

    # resumen de brechas por severidad
    severidades = {"alta": 0, "media": 0, "baja": 0}
    for g in gaps:
        sev = g.get("severidad", "media")
        severidades[sev] = severidades.get(sev, 0) + 1

    constancia = {
        "titulo": "Constancia de Autodiagnóstico de Gobernanza de IA",
        "fecha_evaluacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "organizacion": {
            "perfil": diagnostico.get("perfil", {}).get("descripcion"),
            "pais": org.get("pais"),
            "sector": org.get("sector"),
        },
        "que_se_evaluo": {
            "preguntas_respondidas": verif.get("respondidas"),
            "con_evidencia": verif.get("con_evidencia"),
            "bifurcacion": diagnostico.get("perfil", {}).get("bifurcacion"),
        },
        "que_se_encontro": {
            "vector_diagnostico": v,
            "madurez_nist": diagnostico.get("madurez_nist"),
            "principios_eticos": diagnostico.get("principios_eticos"),
            "brechas_por_severidad": severidades,
            "n_brechas_total": len(gaps),
            "nivel_verificabilidad": verif.get("nivel"),
        },
        "que_se_genero": {
            "recomendaciones": len(recomendaciones),
            "plan_accionable": generar_plan_accionable(recomendaciones)["resumen"],
            "politica_generada": politica is not None,
            "politica_modo": politica.get("modo") if politica else None,
            "politica_citas": len(politica.get("citas", [])) if politica else 0,
        },
        "marco_normativo": {
            "nist_ai_rmf": "1.0",
            "iso_42001": "2023",
            "principios_eticos": "UNESCO + OCDE (Floridi & Cowls 2019)",
        },
        "disclaimer": (
            "Esta constancia refleja el autodiagnóstico declarativo de la organización "
            "en la fecha indicada. El nivel de verificabilidad depende de la evidencia "
            "documental adjunta. No constituye certificación ni reemplaza asesoría legal."
        ),
    }
    return constancia


def constancia_a_markdown(constancia: dict) -> str:
    """Convierte la constancia a Markdown descargable."""
    c = constancia
    org = c["organizacion"]
    ev = c["que_se_evaluo"]
    en = c["que_se_encontro"]
    gen = c["que_se_genero"]
    v = en["vector_diagnostico"]
    sev = en["brechas_por_severidad"]
    mk = c["marco_normativo"]

    lines = [
        f"# {c['titulo']}",
        "",
        f"**Fecha de evaluación:** {c['fecha_evaluacion']}",
        "",
        "## Organización",
        f"- **Perfil:** {org.get('perfil', '—')}",
        f"- **País:** {org.get('pais', '—')}",
        f"- **Sector:** {org.get('sector', '—')}",
        "",
        "## Qué se evaluó",
        f"- **Preguntas respondidas:** {ev['preguntas_respondidas']}",
        f"- **Con evidencia documental:** {ev['con_evidencia']}",
        f"- **Bifurcación:** {ev['bifurcacion']}",
        "",
        "## Qué se encontró",
        f"- **Vector de diagnóstico (x=ÉTICO, y=ISO, z=NIST):** "
        f"({v.get('x_etico')}, {v.get('y_iso')}, {v.get('z_nist')})",
        f"- **Madurez NIST:** {en['madurez_nist']}",
        f"- **Principios éticos:** {en['principios_eticos']}",
        f"- **Brechas por severidad:** {sev.get('alta',0)} altas, "
        f"{sev.get('media',0)} medias, {sev.get('baja',0)} bajas",
        f"- **Total de brechas:** {en['n_brechas_total']}",
        f"- **Nivel de verificabilidad:** {en['nivel_verificabilidad']}",
        "",
        "## Qué se generó",
        f"- **Recomendaciones:** {gen['recomendaciones']}",
        f"- **Plan accionable:** {gen['plan_accionable']['n_tareas']} tareas "
        f"({gen['plan_accionable']['n_quick_wins_0_30']} quick wins 0-30 días)",
        f"- **Política de IA generada:** {'sí' if gen['politica_generada'] else 'no'}"
        + (f" (modo {gen['politica_modo']}, {gen['politica_citas']} citas)" if gen['politica_generada'] else ""),
        "",
        "## Marco normativo aplicado",
        f"- NIST AI RMF {mk['nist_ai_rmf']}",
        f"- ISO/IEC 42001 {mk['iso_42001']}",
        f"- Principios éticos: {mk['principios_eticos']}",
        "",
        "---",
        "",
        f"_{c['disclaimer']}_",
    ]
    return "\n".join(lines)


def plan_a_markdown(plan: dict) -> str:
    """Convierte el plan accionable a Markdown descargable."""
    lines = ["# Plan de Implementación Accionable", ""]
    res = plan["resumen"]
    lines += [
        f"**Total de tareas:** {res['n_tareas']} "
        f"({res['n_quick_wins_0_30']} quick wins · "
        f"{res['n_mediano_plazo_30_90']} mediano plazo · "
        f"{res['n_estructural']} estructural)",
        "",
    ]
    nombres = {"0-30": "Fase 1: 0–30 días (quick wins)",
               "30-90": "Fase 2: 30–90 días",
               "estructural": "Fase 3: Estructural"}
    for fase, tareas in plan["fases"].items():
        if not tareas:
            continue
        lines += [f"## {nombres.get(fase, fase)}", ""]
        for i, t in enumerate(tareas, 1):
            lines += [
                f"### {i}. {t['control']} — {t['brecha']}",
                f"- **Acción:** {t['accion']}",
                f"- **Responsable:** {t['responsable']}",
                f"- **Esfuerzo:** {t['esfuerzo']} | **Severidad:** {t['severidad']} | "
                f"**Prioridad:** {t['prioridad']}",
                f"- **Criterio de cierre:** {t['criterio_cierre']}",
                "",
            ]
    return "\n".join(lines)
