"""
Generador de informe PDF completo para la PYME (WeasyPrint, HTML→PDF).

Integra todo el diagnóstico en un PDF descargable con calidad profesional:
  - Portada
  - Resumen ejecutivo (vector 3D, madurez NIST, ISO, principios, verificabilidad)
  - Brechas detectadas (gap register con severidad, plazo, fuentes)
  - Recomendaciones priorizadas
  - Plan de implementación accionable (3.5)
  - Política de IA (si se generó, 3.1)
  - Constancia verificable (3.6)

WeasyPrint renderiza HTML+CSS a PDF. UTF-8 nativo, tipografía del sistema.
"""

from __future__ import annotations

import html
from datetime import datetime
from typing import Any

from weasyprint import HTML

ETIQUETA_PRINCIPIO = {
    "beneficencia": "Beneficencia",
    "no_maleficencia": "No maleficencia",
    "autonomia": "Autonomía",
    "justicia": "Justicia",
    "explicabilidad": "Explicabilidad",
}

ETIQUETA_NIST = {
    "GOVERN": "Gobernar",
    "MAP": "Mapear",
    "MEASURE": "Medir",
    "MANAGE": "Gestionar",
}

SEV_COLOR = {
    "alta": ("#dc2626", "#fef2f2"),
    "media": ("#d97706", "#fffbeb"),
    "baja": ("#059669", "#ecfdf5"),
}

PLAZO = {
    "alta": "0–30 días",
    "media": "30–90 días",
    "baja": "3–6 meses (estructural)",
}


def _barra_progreso(valor: int | None, color: str = "#6366f1") -> str:
    """Barra de progreso HTML para un valor 0-100."""
    if valor is None:
        return '<div class="bar-bg"><div class="bar-empty">sin datos</div></div>'
    return f'<div class="bar-bg"><div class="bar-fill" style="width:{valor}%;background:{color}"></div></div>'


def _esc(texto: str | None) -> str:
    """Escapa HTML."""
    return html.escape(str(texto or ""))


def generar_informe_html(diag: dict, recs: list[dict],
                         politica: dict | None = None,
                         organizacion: dict | None = None,
                         faithfulness: dict | None = None) -> str:
    """Genera el HTML del informe (con CSS embebido)."""
    org = organizacion or {}
    v = diag.get("diagnostico_vector", {})
    gaps = diag.get("gap_register", [])
    madurez = diag.get("madurez_nist", {})
    principios = diag.get("principios_eticos", {})
    cobertura = diag.get("cobertura_iso", [])
    verif = diag.get("verificabilidad", {})

    score = None
    if v.get("x_etico") is not None and v.get("y_iso") is not None and v.get("z_nist") is not None:
        score = round((v["x_etico"] + v["y_iso"] + v["z_nist"]) / 3)

    n_altas = sum(1 for g in gaps if g["severidad"] == "alta")
    n_medias = sum(1 for g in gaps if g["severidad"] == "media")
    n_bajas = sum(1 for g in gaps if g["severidad"] == "baja")

    #CSS embebido
    css = """
    @page { size: A4; margin: 2cm 2.5cm;
        @bottom-center { content: "Página " counter(page) " de " counter(pages); font-size: 9px; color: #94a3b8; }
        @top-right { content: "Playbook de IA Responsable"; font-size: 9px; color: #94a3b8; }
    }
    @page :first { margin-top: 4cm; @top-right { content: ""; } @bottom-center { content: ""; } }
    body { font-family: 'DejaVu Sans', sans-serif; font-size: 11px; color: #1e293b; line-height: 1.5; }
    h1 { font-size: 24px; color: #4f46e5; margin: 0 0 8px; }
    h2 { font-size: 16px; color: #4f46e5; border-bottom: 2px solid #e0e7ff; padding-bottom: 4px; margin: 24px 0 12px; }
    h3 { font-size: 13px; color: #1e293b; margin: 16px 0 6px; }
    p { margin: 4px 0; }
    .portada { text-align: center; margin-top: 60px; }
    .portada h1 { font-size: 32px; margin-bottom: 20px; }
    .portada .sub { font-size: 14px; color: #64748b; margin: 8px 0; }
    .portada .fecha { font-size: 12px; color: #94a3b8; margin-top: 16px; }
    .portada .disclaimer { font-size: 9px; color: #94a3b8; margin-top: 60px; font-style: italic; }
    .cards { display: flex; gap: 10px; margin: 12px 0; }
    .card { flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; }
    .card .label { font-size: 9px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    .card .value { font-size: 13px; color: #1e293b; font-weight: bold; margin-top: 4px; }
    .vector-box { background: linear-gradient(135deg, #eef2ff, #faf5ff); border: 1px solid #e0e7ff; border-radius: 8px; padding: 14px; margin: 12px 0; }
    .vector-box strong { color: #4f46e5; }
    .bar-bg { background: #e2e8f0; border-radius: 4px; height: 18px; width: 100%; margin: 4px 0; position: relative; }
    .bar-fill { height: 100%; border-radius: 4px; }
    .bar-empty { position: absolute; top: 2px; left: 8px; font-size: 9px; color: #94a3b8; }
    .metric-row { display: flex; align-items: center; gap: 8px; margin: 6px 0; }
    .metric-row .name { width: 140px; font-size: 11px; }
    .metric-row .bar { flex: 1; }
    .metric-row .num { width: 40px; text-align: right; font-weight: bold; font-size: 11px; }
    .sev-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 9px; font-weight: bold; color: white; }
    .sev-alta { background: #dc2626; }
    .sev-media { background: #d97706; }
    .sev-baja { background: #059669; }
    .gap-card { border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin: 10px 0; page-break-inside: avoid; }
    .gap-header { display: flex; justify-content: space-between; align-items: flex-start; }
    .gap-title { font-weight: bold; font-size: 12px; margin: 4px 0; }
    .gap-desc { font-size: 10px; color: #64748b; margin: 4px 0; }
    .plazo-badge { padding: 4px 10px; border-radius: 6px; font-size: 10px; font-weight: bold; border: 1px solid; }
    .fuentes { margin-top: 8px; padding-top: 8px; border-top: 1px solid #f1f5f9; font-size: 10px; }
    .fuente-row { margin: 3px 0; }
    .fuente-label { color: #94a3b8; font-size: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
    .rec-card { border-left: 3px solid #6366f1; padding: 8px 12px; margin: 8px 0; background: #f8fafc; page-break-inside: avoid; }
    .rec-title { font-weight: bold; font-size: 11px; }
    .rec-desc { font-size: 10px; color: #475569; margin: 4px 0; }
    .rec-meta { font-size: 9px; color: #94a3b8; }
    .plan-fase { margin: 16px 0; }
    .plan-fase h3 { color: #4f46e5; }
    .plan-task { border: 1px solid #e2e8f0; border-radius: 4px; padding: 8px; margin: 6px 0; page-break-inside: avoid; }
    .politica-text { white-space: pre-wrap; font-size: 10px; line-height: 1.6; background: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0; }
    .faithfulness-box { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 10px; margin: 10px 0; }
    .faithfulness-box.warn { background: #fefce8; border-color: #fde68a; }
    .kv { margin: 4px 0; font-size: 11px; }
    .kv .k { font-weight: bold; color: #1e293b; display: inline-block; width: 160px; }
    .kv .v { color: #475569; }
    ul { margin: 4px 0; padding-left: 20px; }
    li { margin: 3px 0; font-size: 11px; }
    .leyenda { font-size: 10px; color: #64748b; margin: 10px 0; padding: 8px; background: #f8fafc; border-radius: 4px; }
    .pagebreak { page-break-before: always; }
    """

    # Construir HTML
    parts = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>"]

    # ---------- PORTADA ----------
    parts.append(f"""
    <div class="portada">
      <h1>Informe de Autodiagnóstico<br/>de Gobernanza de IA</h1>
      <div class="sub">{_esc(org.get('perfil') or 'Organización')}</div>
      <div class="sub">País: {_esc(org.get('pais') or '—')}  ·  Sector: {_esc(org.get('sector') or '—')}</div>
      <div class="fecha">Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
      <div class="disclaimer">Este informe refleja el autodiagnóstico declarativo de la organización.
      El nivel de verificabilidad depende de la evidencia documental adjunta.
      No constituye certificación ni reemplaza asesoría legal profesional.</div>
    </div>
    """)

    # ---------- RESUMEN EJECUTIVO ----------
    parts.append('<div class="pagebreak"></div>')
    parts.append("<h1>1. Resumen ejecutivo</h1>")

    if score is not None:
        parts.append(f"""
        <div class="vector-box">
          <p>Su organización se ubica en el vector <strong>(x=ÉTICO {v['x_etico']}, y=ISO {v['y_iso']}, z=NIST {v['z_nist']})</strong>
          sobre 100. <strong>Score global: {score}/100.</strong></p>
        """)
        if score < 40:
            parts.append("<p>Su organización está en zona de riesgo — conviene priorizar las brechas altas.</p>")
        elif score <= 70:
            parts.append("<p>Su organización tiene una base, pero hay brechas importantes que atender.</p>")
        else:
            parts.append("<p>Su organización tiene un nivel sólido — mantenga las prácticas y cierre las brechas restantes.</p>")
        parts.append("</div>")
    else:
        parts.append("<p>Sin datos suficientes para calcular el vector de diagnóstico.</p>")

    # Cards de resumen
    parts.append(f"""
    <div class="cards">
      <div class="card"><div class="label">Brechas totales</div><div class="value">{len(gaps)}</div></div>
      <div class="card"><div class="label">Altas</div><div class="value" style="color:#dc2626">{n_altas}</div></div>
      <div class="card"><div class="label">Medias</div><div class="value" style="color:#d97706">{n_medias}</div></div>
      <div class="card"><div class="label">Bajas</div><div class="value" style="color:#059669">{n_bajas}</div></div>
    </div>
    <div class="cards">
      <div class="card"><div class="label">Verificabilidad</div><div class="value">{_esc(verif.get('nivel','—'))}</div></div>
      <div class="card"><div class="label">Respuestas</div><div class="value">{verif.get('respondidas',0)}</div></div>
      <div class="card"><div class="label">Con evidencia</div><div class="value">{verif.get('con_evidencia',0)}</div></div>
      <div class="card"><div class="label">Recomendaciones</div><div class="value">{len(recs)}</div></div>
    </div>
    """)

    # Madurez NIST con barras
    parts.append("<h3>Madurez por función NIST AI RMF</h3>")
    for fn in ["GOVERN", "MAP", "MEASURE", "MANAGE"]:
        val = madurez.get(fn)
        etiqueta = ETIQUETA_NIST.get(fn, fn)
        parts.append(f'<div class="metric-row"><div class="name">{etiqueta}</div><div class="bar">{_barra_progreso(val)}</div><div class="num">{val if val is not None else "—"}</div></div>')

    # ISO por área
    parts.append("<h3>Cobertura ISO 42001 por área</h3>")
    areas = {}
    for c in cobertura:
        pref = c["id_control"][:3]
        areas.setdefault(pref, []).append(c.get("puntaje", 0))
    nombres_area = {"A.2": "Política", "A.3": "Roles", "A.5": "Evaluación de impacto",
                    "A.6": "Datos", "A.7": "Documentación", "A.8": "Operación",
                    "A.9": "Supervisión", "A.10": "Terceros e incidentes"}
    for pref, puntajes in areas.items():
        prom = round(sum(puntajes) / len(puntajes)) if puntajes else 0
        nombre = nombres_area.get(pref, pref)
        parts.append(f'<div class="metric-row"><div class="name">{nombre}</div><div class="bar">{_barra_progreso(prom, "#0ea5e9")}</div><div class="num">{prom}</div></div>')

    # Principios éticos
    parts.append("<h3>Principios éticos (UNESCO + OCDE)</h3>")
    for p in ["beneficencia", "no_maleficencia", "autonomia", "justicia", "explicabilidad"]:
        val = principios.get(p)
        etiqueta = ETIQUETA_PRINCIPIO.get(p, p)
        parts.append(f'<div class="metric-row"><div class="name">{etiqueta}</div><div class="bar">{_barra_progreso(val, "#9333ea")}</div><div class="num">{val if val is not None else "—"}</div></div>')

    # Leyenda de plazos
    parts.append(f"""
    <div class="leyenda">
      <strong>Plazos de implementación según gravedad:</strong><br/>
      <span class="sev-badge sev-alta">Alta</span> → {PLAZO['alta']} &nbsp;·&nbsp;
      <span class="sev-badge sev-media">Media</span> → {PLAZO['media']} &nbsp;·&nbsp;
      <span class="sev-badge sev-baja">Baja</span> → {PLAZO['baja']}
    </div>
    """)

    # ---------- GAP REGISTER ----------
    if gaps:
        parts.append('<div class="pagebreak"></div>')
        parts.append("<h1>2. Brechas detectadas (gap register)</h1>")
        parts.append("<p>Cada brecha indica el control ISO 42001 afectado, su severidad, el plazo recomendado de implementación y las fuentes normativas exactas.</p>")
        for g in gaps:
            color, bg = SEV_COLOR.get(g["severidad"], ("#64748b", "#f1f5f9"))
            plazo = g.get("plazo") or PLAZO.get(g["severidad"], "—")
            nist_tags = g.get("nist", [])
            nist_txt = ", ".join(f"{fn} ({ETIQUETA_NIST.get(fn, fn)})" for fn in nist_tags) if nist_tags else "—"
            clausula = g.get("clausula", "")
            iso_txt = f"Anexo A · {g['id_control']}" + (f" (cláusula {clausula})" if clausula else "")
            principios_g = g.get("principios", [])
            princ_txt = " · ".join(ETIQUETA_PRINCIPIO.get(p, p) for p in principios_g) if principios_g else "—"
            parts.append(f"""
            <div class="gap-card">
              <div class="gap-header">
                <div>
                  <span class="sev-badge sev-{g['severidad']}">{g['severidad'].upper()}</span>
                  <span style="font-family:monospace;font-size:10px;color:#64748b;margin-left:6px;">ISO 42001 · {g['id_control']}</span>
                </div>
                <div class="plazo-badge" style="color:{color};border-color:{color};background:{bg};">Implementar en: {plazo}</div>
              </div>
              <div class="gap-title">{_esc(g['nombre'])}</div>
              <div class="gap-desc">{_esc(g.get('descripcion',''))}</div>
              <div class="fuentes">
                <div class="fuente-row"><span class="fuente-label">NIST AI RMF</span><br/>{_esc(nist_txt)}</div>
                <div class="fuente-row"><span class="fuente-label">ISO/IEC 42001</span><br/>{_esc(iso_txt)}</div>
                <div class="fuente-row"><span class="fuente-label">Principios éticos</span><br/>{_esc(princ_txt)}</div>
              </div>
            </div>
            """)

    # ---------- RECOMENDACIONES ----------
    if recs:
        parts.append('<div class="pagebreak"></div>')
        parts.append("<h1>3. Recomendaciones priorizadas</h1>")
        parts.append("<p>Ordenadas por prioridad (reducción de riesgo / esfuerzo). Las prioridades más altas son quick wins de alto impacto.</p>")
        for i, r in enumerate(recs, 1):
            parts.append(f"""
            <div class="rec-card">
              <div class="rec-title">{i}. {_esc(r.get('brecha', r.get('id_control','')))} <span style="color:#6366f1">(prioridad {r.get('prioridad','—')})</span></div>
              <div class="rec-desc">{_esc(r.get('recomendacion',''))}</div>
              <div class="rec-meta">Esfuerzo: {_esc(r.get('esfuerzo','—'))} · Fase: {_esc(r.get('fase','—'))} · Rol: {_esc(r.get('rol','—'))}</div>
              <div class="rec-meta">Criterio de cierre: {_esc(r.get('criterio_cierre','—'))}</div>
            </div>
            """)

    # ---------- PLAN ACCIONABLE ----------
    if recs:
        parts.append('<div class="pagebreak"></div>')
        parts.append("<h1>4. Plan de implementación accionable</h1>")
        parts.append("<p>Tareas asignables agrupadas por fase temporal.</p>")
        from artifacts import generar_plan_accionable
        plan = generar_plan_accionable(recs)
        nombres = {"0-30": "Fase 1: 0–30 días (quick wins)", "30-90": "Fase 2: 30–90 días", "estructural": "Fase 3: Estructural (3–6 meses)"}
        for fase, tareas in plan["fases"].items():
            if not tareas:
                continue
            parts.append(f'<div class="plan-fase"><h3>{nombres.get(fase, fase)}</h3>')
            for j, t in enumerate(tareas, 1):
                parts.append(f"""
                <div class="plan-task">
                  <div class="rec-title">{j}. {t['control']} — {_esc(t['brecha'])}</div>
                  <div class="rec-desc">Acción: {_esc(t['accion'])}</div>
                  <div class="rec-meta">Responsable: {_esc(t['responsable'])} · Esfuerzo: {_esc(t['esfuerzo'])} · Severidad: {_esc(t['severidad'])}</div>
                  <div class="rec-meta">Cierre: {_esc(t['criterio_cierre'])}</div>
                </div>
                """)
            parts.append("</div>")

    # ---------- POLÍTICA ----------
    if politica and politica.get("texto"):
        parts.append('<div class="pagebreak"></div>')
        parts.append("<h1>5. Política de IA generada</h1>")
        modo = politica.get("modo", "—")
        parts.append(f"<p><strong>Modo de generación:</strong> {modo}</p>")
        if faithfulness and faithfulness.get("score") is not None:
            f_score = faithfulness["score"] * 100
            cls = "faithfulness-box" if faithfulness.get("faithful") else "faithfulness-box warn"
            parts.append(f"""
            <div class="{cls}">
              <strong>Faithfulness (LLM-as-judge): {f_score:.1f}%</strong> —
              {faithfulness.get('n_faithful',0)} afirmaciones fieles de {faithfulness.get('n_claims',0)} totales.
              {'✓ Política respaldada por las fuentes.' if faithfulness.get('faithful') else f"⚠ {faithfulness.get('n_unfaithful',0)} afirmaciones no respaldadas detectadas."}
            </div>
            """)
        parts.append(f'<div class="politica-text">{_esc(politica["texto"])}</div>')
        citas = politica.get("citas", [])
        if citas:
            parts.append("<h3>Fuentes citadas</h3><ul>")
            for c in citas:
                parts.append(f"<li>{_esc(c.get('fuente','—'))}</li>")
            parts.append("</ul>")

    # ---------- CONSTANCIA ----------
    parts.append('<div class="pagebreak"></div>')
    parts.append("<h1>6. Constancia verificable</h1>")
    from artifacts import generar_constancia
    const = generar_constancia(diag, recs, politica, org)
    parts.append(f"<p><strong>Fecha de evaluación:</strong> {const['fecha_evaluacion']}</p>")
    parts.append("<h3>Organización</h3>")
    for k, label in [("perfil", "Perfil"), ("pais", "País"), ("sector", "Sector")]:
        parts.append(f'<div class="kv"><span class="k">{label}:</span><span class="v">{_esc(const["organizacion"].get(k) or "—")}</span></div>')
    parts.append("<h3>Qué se evaluó</h3>")
    ev = const["que_se_evaluo"]
    parts.append(f'<div class="kv"><span class="k">Preguntas respondidas:</span><span class="v">{ev["preguntas_respondidas"]}</span></div>')
    parts.append(f'<div class="kv"><span class="k">Con evidencia:</span><span class="v">{ev["con_evidencia"]}</span></div>')
    parts.append("<h3>Qué se encontró</h3>")
    en = const["que_se_encontro"]
    vec = en["vector_diagnostico"]
    parts.append(f'<div class="kv"><span class="k">Vector (x,y,z):</span><span class="v">({vec.get("x_etico")}, {vec.get("y_iso")}, {vec.get("z_nist")})</span></div>')
    parts.append(f'<div class="kv"><span class="k">Brechas totales:</span><span class="v">{en["n_brechas_total"]}</span></div>')
    sev = en["brechas_por_severidad"]
    parts.append(f'<div class="kv"><span class="k">Por severidad:</span><span class="v">{sev.get("alta",0)} altas, {sev.get("media",0)} medias, {sev.get("baja",0)} bajas</span></div>')
    parts.append(f'<div class="kv"><span class="k">Verificabilidad:</span><span class="v">{_esc(en["nivel_verificabilidad"])}</span></div>')
    parts.append("<h3>Qué se generó</h3>")
    gen = const["que_se_genero"]
    parts.append(f'<div class="kv"><span class="k">Recomendaciones:</span><span class="v">{gen["recomendaciones"]}</span></div>')
    parts.append(f'<div class="kv"><span class="k">Plan accionable:</span><span class="v">{gen["plan_accionable"]["n_tareas"]} tareas</span></div>')
    parts.append(f'<div class="kv"><span class="k">Política de IA:</span><span class="v">{"sí" if gen["politica_generada"] else "no"}</span></div>')
    parts.append("<h3>Marco normativo</h3><ul>")
    mk = const["marco_normativo"]
    parts.append(f"<li>NIST AI RMF {mk['nist_ai_rmf']}</li>")
    parts.append(f"<li>ISO/IEC 42001 {mk['iso_42001']}</li>")
    parts.append(f"<li>{_esc(mk['principios_eticos'])}</li>")
    parts.append("</ul>")
    parts.append(f'<p style="font-size:9px;color:#94a3b8;font-style:italic;margin-top:20px;">{_esc(const["disclaimer"])}</p>')

    parts.append("</body></html>")
    return "".join(parts)


def generar_informe_pdf(diag: dict, recs: list[dict],
                        politica: dict | None = None,
                        organizacion: dict | None = None,
                        faithfulness: dict | None = None) -> bytes:
    """Genera el informe PDF completo. Devuelve los bytes del PDF."""
    html_str = generar_informe_html(diag, recs, politica, organizacion, faithfulness)
    return HTML(string=html_str).write_pdf()
