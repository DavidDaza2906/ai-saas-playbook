"""
Motor determinista del diagnóstico (Capa 1) y recomendaciones (Capa 2).

No usa LLM ni red: es el espinazo fiable y auditable del sistema. Toma las
respuestas del árbol y produce un diagnóstico reproducible, mapeando cada
respuesta a funciones/subcategorías NIST, controles ISO 42001 y principios
éticos mediante las etiquetas que las preguntas ya traen.

DISEÑO CLAVE: el motor es 100% data-driven. No conoce ningún ID de pregunta
concreto ni asume un vocabulario de respuesta fijo. Las preguntas se cargan
desde questions.json siguiendo el contrato documentado en
data/SCHEMA_PREGUNTAS.md y el sistema funciona sin tocar este archivo.

Soporta:
- Preguntas base + subpreguntas anidadas (condicionadas a la respuesta del padre).
- Tipos: multiple, multiple_seleccion, likert, numero (tramos), matriz (tabla),
  texto (no puntúa) y estado (legacy).
- Vector de diagnóstico 3D (x=ÉTICO, y=ISO, z=NIST) por promedio ponderado.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).parent / "data"

# Fuentes ligadas a un país (paquete nacional). El resto es universal (pais=None):
# NIST, ISO 42001, y los 5 principios éticos consolidados (UNESCO + OCDE).
# Actualmente vacío: el sistema opera con corpus normativo universal.
PAIS_POR_FUENTE = {}

PRINCIPIOS = ["beneficencia", "no_maleficencia", "autonomia", "justicia", "explicabilidad"]
FUNCIONES_NIST = ["GOVERN", "MAP", "MEASURE", "MANAGE"]

_ESFUERZO_PESO = {"bajo": 1, "medio": 2, "alto": 3}
_SEVERIDAD_PESO = {"alta": 3, "media": 2, "baja": 1}

# Severidad base por control: refleja cuán crítico es el control para derechos/ley.
# Alineado a las definiciones de controls.json (que siguen ARBOL_PREGUNTAS.md).
SEVERIDAD_BASE = {
    "A.6.2": "alta", "A.5.1": "alta", "A.5.3": "alta", "A.9.2": "alta",
    "A.2.2": "media", "A.3.2": "media", "A.5.2": "media", "A.5.4": "media",
    "A.7.2": "media", "A.8.2": "media", "A.8.5": "media",
    "A.10.2": "media", "A.10.3": "media",
    "A.2.3": "baja",
}

PERFILES = {
    "1": "Desarrolla o usa IA para productos o servicios para terceros",
    "2": "Utiliza IA para automatizar procesos internos",
    "3": "Desarrolla productos con IA y automatiza procesos internos",
}


@lru_cache(maxsize=1)
def load_data() -> dict[str, Any]:
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    controls = json.loads((DATA / "controls.json").read_text(encoding="utf-8"))
    recommendations = json.loads((DATA / "recommendations.json").read_text(encoding="utf-8"))
    corpus = []
    for f in sorted((DATA / "corpus").glob("*.json")):
        chunks = json.loads(f.read_text(encoding="utf-8"))
        pais = PAIS_POR_FUENTE.get(f.stem)
        for c in chunks:
            c.setdefault("pais", pais)  # respeta el pais explícito si ya viene
        corpus.extend(chunks)
    return {"questions": questions, "controls": controls,
            "recommendations": recommendations, "corpus": corpus}


# ---------------------------------------------------------------------------
# Helpers data-driven (sin IDs ni vocabularios cableados)
# ---------------------------------------------------------------------------

def _opciones(q: dict, data: dict) -> list[dict]:
    """Opciones de una pregunta: propias si las trae, o el set 'estado' por defecto."""
    if "opciones" in q:
        return q["opciones"]
    if q.get("tipo") == "estado":
        return data["questions"]["estado_opciones"]
    return []


def _puntaje(q: dict, data: dict, valor: str | list | int | None) -> float | None:
    """Puntaje normalizado 0..1 de una respuesta, según el tipo de pregunta.

    - multiple / likert / estado: valor = string; puntaje de la opción / max.
    - multiple_seleccion: valor = lista de strings; promedia y normaliza.
    - numero: valor = int o 'ns'; discretiza por tramos; puntaje del tramo.
    - matriz: valor = lista de strings (uno por fila); agrega (peor/promedio).
    - texto: no puntúa → None.
    - Devuelve None si no aplica (na), no hay respuesta, o no puntúa.
    """
    if valor is None:
        return None
    tipo = q.get("tipo", "estado")

    if tipo == "texto":
        return None

    if tipo == "numero":
        return _puntaje_numero(q, valor)

    if tipo == "matriz":
        return _puntaje_matriz(q, valor)

    opts = {o["valor"]: o.get("puntaje") for o in _opciones(q, data)}
    seleccionados = valor if isinstance(valor, list) else [valor]
    crudos = [opts[v] for v in seleccionados if opts.get(v) is not None]
    if not crudos:
        return None
    techo = max((p for p in opts.values() if p is not None), default=1.0) or 1.0
    return (sum(crudos) / len(crudos)) / techo


def _puntaje_numero(q: dict, valor) -> float | None:
    """Discretiza un número por tramos. valor = int o 'ns'."""
    tramos = q.get("tramos", [])
    if not tramos:
        return None
    if valor == "ns" or valor is None:
        for t in tramos:
            if t.get("hasta") is None:
                return t.get("puntaje")
        return None
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return None
    for t in tramos:
        hasta = t.get("hasta")
        if hasta is not None and n <= hasta:
            return t.get("puntaje")
    # si ningún tramo numérico cupo, devolver el tramo sin 'hasta' (ns/otros)
    for t in tramos:
        if t.get("hasta") is None:
            return t.get("puntaje")
    return None


def _valor_tramo(q: dict, valor) -> str | None:
    """El valor_tramo asignado a una respuesta numérica (para condiciones de otras preguntas)."""
    if valor is None:
        return None
    tramos = q.get("tramos", [])
    if valor == "ns":
        for t in tramos:
            if t.get("hasta") is None:
                return t.get("valor_tramo")
        return None
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return None
    for t in tramos:
        hasta = t.get("hasta")
        if hasta is not None and n <= hasta:
            return t.get("valor_tramo")
    for t in tramos:
        if t.get("hasta") is None:
            return t.get("valor_tramo")
    return None


def _puntaje_matriz(q: dict, valor: list) -> float | None:
    """Agrega los puntajes de las filas. 'peor' = min, 'promedio' = media."""
    if not isinstance(valor, list) or not valor:
        return None
    opts = {o["valor"]: o.get("puntaje") for o in q.get("opciones", [])}
    crudos = [opts[v] for v in valor if opts.get(v) is not None]
    if not crudos:
        return None
    agregacion = q.get("agregacion", "peor")
    if agregacion == "promedio":
        base = sum(crudos) / len(crudos)
    else:  # peor
        base = min(crudos)
    techo = max((p for p in opts.values() if p is not None), default=1.0) or 1.0
    return base / techo


def _valor_efectivo(q: dict, valor) -> str | list | None:
    """El valor que se usa para condiciones de otras preguntas.
    Para tipo 'numero', devuelve el valor_tramo (string discretizado).
    Para los demás, devuelve valor tal cual."""
    if q.get("tipo") == "numero":
        return _valor_tramo(q, valor)
    return valor


def _pesos(q: dict) -> dict[str, float]:
    """Pesos de la pregunta por eje (etico, iso, nist).
    Usa el campo fijo 'pesos' si existe (congelado en diseño vía RAG); si no,
    los deriva del 'mapeo' (binario: 1 si la pregunta toca el eje, 0 si no)."""
    if "pesos" in q:
        pz = q["pesos"]
        return {"etico": pz.get("etico", 0.0), "iso": pz.get("iso", 0.0), "nist": pz.get("nist", 0.0)}
    m = q.get("mapeo", {})
    return {
        "etico": 1.0 if m.get("principio") else 0.0,
        "iso": 1.0 if m.get("iso") else 0.0,
        "nist": 1.0 if m.get("nist") else 0.0,
    }


def _condicion_ok(q: dict, respuestas: dict) -> bool:
    """Ramas por respuesta previa. 'condicion' = {pregunta, en:[...], modo?} o lista (AND).
    Para preguntas tipo 'numero', la condición compara contra valor_tramo del padre.
    Para tipo 'matriz', contra el valor agregado (peor caso).
    Para tipo 'multiple_seleccion' (respuesta lista), 'modo: alguna|todas' (default: alguna)."""
    cond = q.get("condicion")
    if not cond:
        return True
    conds = cond if isinstance(cond, list) else [cond]
    for c in conds:
        pid = c.get("pregunta")
        esperado = c.get("en", [])
        actual = respuestas.get(pid)
        if isinstance(actual, list):
            modo = c.get("modo", "alguna")
            if modo == "todas":
                ok = all(e in actual for e in esperado)
            else:  # alguna
                ok = any(e in actual for e in esperado)
            if not ok:
                return False
        else:
            if actual not in esperado:
                return False
    return True


def _valor_agregado_matriz(q: dict, valor: list) -> str | None:
    """Para condiciones de preguntas dependientes: el valor de la opción con menor
    puntaje (peor caso). Ej. matriz con [bajo, alto, medio] → 'alto'."""
    if not isinstance(valor, list) or not valor:
        return None
    opts = {o["valor"]: o for o in q.get("opciones", [])}
    presentes = [opts[v] for v in valor if v in opts and opts[v].get("puntaje") is not None]
    if not presentes:
        return None
    peor = min(presentes, key=lambda o: o.get("puntaje", 0))
    return peor["valor"]


def _aplicables(data: dict, bifurcacion: str, respuestas: dict) -> list[dict]:
    """Preguntas vigentes: por bifurcación (ramas) y por respuestas previas (condicion).
    Aplana subpreguntas activas en la lista principal (cada una con su ramas heredadas).
    Las respuestas 'numero' se discretizan a valor_tramo y las 'matriz' a su valor
    agregado (peor caso), para que las condiciones de preguntas dependientes funcionen."""
    resp_disc = dict(respuestas)
    preguntas_base = data["questions"]["preguntas"]
    by_id = {p["id"]: p for p in preguntas_base}
    for pid, p in by_id.items():
        val = respuestas.get(pid)
        if val is None:
            continue
        if p.get("tipo") == "numero":
            vt = _valor_tramo(p, val)
            if vt is not None:
                resp_disc[pid] = vt
        elif p.get("tipo") == "matriz" and isinstance(val, list):
            agg = _valor_agregado_matriz(p, val)
            if agg is not None:
                resp_disc[pid] = agg

    resultado: list[dict] = []
    for q in preguntas_base:
        if bifurcacion not in q.get("ramas", []):
            continue
        if not _condicion_ok(q, resp_disc):
            continue
        resultado.append(q)
        # subpreguntas (1 nivel)
        for sub in q.get("subpreguntas", []):
            sub_ram = sub.get("ramas", q.get("ramas", []))  # hereda ramas
            if bifurcacion not in sub_ram:
                continue
            if not _condicion_ok(sub, resp_disc):
                continue
            resultado.append(sub)
            # subpreguntas de 2º nivel
            for sub2 in sub.get("subpreguntas", []):
                sub2_ram = sub2.get("ramas", sub_ram)
                if bifurcacion not in sub2_ram:
                    continue
                if not _condicion_ok(sub2, resp_disc):
                    continue
                resultado.append(sub2)
    return resultado


def _funcion_nist(tag: str) -> str:
    """'GOVERN-1.1' o 'GOVERN.1.1' -> 'GOVERN'. 'GOVERN' -> 'GOVERN'."""
    return re.split(r"[-.]", tag, maxsplit=1)[0]


# ---------------------------------------------------------------------------
# CAPA 1 — Diagnóstico
# ---------------------------------------------------------------------------

def diagnosticar(bifurcacion: str, respuestas: dict[str, Any],
                 evidencias: list[str] | None = None) -> dict[str, Any]:
    data = load_data()
    evidencias = set(evidencias or [])
    preguntas = _aplicables(data, bifurcacion, respuestas)

    func_scores: dict[str, list[float]] = {fn: [] for fn in FUNCIONES_NIST}
    sub_scores: dict[str, list[float]] = {}          # 1.3 desagregación por subcategoría
    princ_scores: dict[str, list[float]] = {p: [] for p in PRINCIPIOS}
    control_estado: dict[str, str] = {}
    control_meta: dict[str, dict] = {}
    inventario: list[dict] = []
    texto_abierto: dict[str, str] = {}
    # Promedio ponderado del vector (x,y,z): numerador y denominador por eje.
    vec_num = {"etico": 0.0, "iso": 0.0, "nist": 0.0}
    vec_den = {"etico": 0.0, "iso": 0.0, "nist": 0.0}

    for q in preguntas:
        valor = respuestas.get(q["id"])
        tipo = q.get("tipo", "estado")

        # Texto abierto: se guarda pero no puntúa
        if tipo == "texto":
            if valor:
                texto_abierto[q["id"]] = valor
            continue

        p = _puntaje(q, data, valor)
        mapeo = q.get("mapeo", {})

        # 1.2 Inventario de casos de uso
        # (a) vía etiqueta caso_uso de la pregunta
        cu = q.get("caso_uso")
        if cu and valor in cu.get("cuando", []):
            inventario.append({"caso": cu["caso"], "riesgo": cu["riesgo"]})
        # (b) vía tipo matriz: cada fila con alto/medio es un caso de uso
        if tipo == "matriz" and isinstance(valor, list):
            opts = {o["valor"]: o for o in q.get("opciones", [])}
            for v in valor:
                if v in ("alto", "medio", "bajo"):
                    inventario.append({"caso": q.get("texto", "Sistema de IA"),
                                       "riesgo": v})

        if p is None:  # na / sin responder no puntúa pero sí pudo aportar inventario
            continue

        # Vector 3D: acumula promedio ponderado por eje (pesos fijos o derivados del mapeo)
        for eje, w in _pesos(q).items():
            if w > 0:
                vec_num[eje] += p * w
                vec_den[eje] += w

        # 1.3 Madurez NIST por función y subcategoría
        for tag in mapeo.get("nist", []):
            func_scores.setdefault(_funcion_nist(tag), []).append(p)
            if tag not in FUNCIONES_NIST:
                sub_scores.setdefault(tag, []).append(p)

        # Eje ético por principio (UNESCO + OCDE; Floridi)
        for pr in mapeo.get("principio", []):
            princ_scores.setdefault(pr, []).append(p)

        # 1.4 estado por control ISO (peor estado gana)
        for ctrl in mapeo.get("iso", []):
            if ctrl not in control_estado or p < control_meta.get(ctrl, {}).get("p", 1.1):
                control_estado[ctrl] = valor
                control_meta.setdefault(ctrl, {})
                control_meta[ctrl]["p"] = min(p, control_meta.get(ctrl, {}).get("p", 1.1))
            meta = control_meta.setdefault(ctrl, {})
            meta.setdefault("principios", set()).update(mapeo.get("principio", []))
            meta.setdefault("nist", set()).update(_funcion_nist(t) for t in mapeo.get("nist", []))

    def _media(vs: list[float]) -> int | None:
        # Mínimo de 2 preguntas puntuadas para reportar madurez; con 0-1 el
        # promedio es ruidoso (una sola pregunta aislada daría 0% o 100%).
        if len(vs) < 2:
            return None
        return round(100 * sum(vs) / len(vs)) if vs else None

    madurez_nist = {fn: _media(v) for fn, v in func_scores.items()}
    subcategorias_nist = {tag: _media(v) for tag, v in sub_scores.items()}
    principios_eticos = {p: _media(v) for p, v in princ_scores.items()}

    # 1.4 Cobertura + 1.5 Gap register
    iso_index = {c["id"]: c for c in data["controls"]["iso_controls"]}
    cobertura_iso, gap_register = [], []
    for ctrl, valor in control_estado.items():
        info = iso_index.get(ctrl, {})
        p = control_meta[ctrl]["p"]
        estado = "implementado" if p >= 1.0 else ("parcial" if p > 0 else "ausente")
        cobertura_iso.append({"id_control": ctrl, "nombre": info.get("nombre", ctrl),
                              "clausula": info.get("clausula"), "estado": estado,
                              "puntaje": round(100 * p)})
        if p < 1.0:
            sev = SEVERIDAD_BASE.get(ctrl, "media")
            if estado == "parcial" and sev == "alta":
                sev = "media"
            meta = control_meta[ctrl]
            ejes = ["ISO"] + (["NIST"] if meta.get("nist") else []) + (["ETICO"] if meta.get("principios") else [])
            # Plazo de implementación según severidad (para el plan y el gap register)
            plazo = {"alta": "0-30 días", "media": "30-90 días", "baja": "3-6 meses (estructural)"}[sev]
            gap_register.append({
                "id_control": ctrl,
                "nombre": info.get("nombre", ctrl),
                "descripcion": info.get("descripcion", ""),
                "clausula": info.get("clausula"),
                "estado": estado,
                "severidad": sev,
                "plazo": plazo,
                "ejes": ejes,
                "nist": sorted(meta.get("nist", set())),
                "principios": sorted(meta.get("principios", set())),
            })
    gap_register.sort(key=lambda g: _SEVERIDAD_PESO[g["severidad"]], reverse=True)

    # 1.6 Verificabilidad
    respondidas = [q for q in preguntas if respuestas.get(q["id"]) is not None
                   and q.get("tipo") != "texto"]
    con_evidencia = [q for q in respondidas if q["id"] in evidencias]
    verificabilidad = {
        "respondidas": len(respondidas),
        "con_evidencia": len(con_evidencia),
        "nivel": _nivel_verificabilidad(len(con_evidencia), len(respondidas)),
        "detalle": {q["id"]: ("verificado" if q["id"] in evidencias else "autodeclarado")
                    for q in respondidas},
    }

    # Vector de diagnóstico (x, y, z) = (ÉTICO, ISO, NIST): promedio ponderado
    # normalizado por la suma de pesos de las preguntas efectivamente puntuadas.
    def _eje(k: str) -> int | None:
        return round(100 * vec_num[k] / vec_den[k]) if vec_den[k] else None

    diagnostico_vector = {
        "x_etico": _eje("etico"),
        "y_iso": _eje("iso"),
        "z_nist": _eje("nist"),
    }

    # Deduplica el inventario (puede haber duplicados de matriz + caso_uso)
    visto = set()
    inventario_uniq = []
    for it in inventario:
        k = (it["caso"], it["riesgo"])
        if k not in visto:
            visto.add(k)
            inventario_uniq.append(it)

    return {
        "perfil": {"bifurcacion": bifurcacion, "descripcion": PERFILES.get(bifurcacion, "")},
        "inventario": inventario_uniq,
        "diagnostico_vector": diagnostico_vector,
        "madurez_nist": madurez_nist,
        "subcategorias_nist": subcategorias_nist,
        "principios_eticos": principios_eticos,
        "cobertura_iso": cobertura_iso,
        "gap_register": gap_register,
        "verificabilidad": verificabilidad,
        "texto_abierto": texto_abierto,
    }


def _nivel_verificabilidad(con_evidencia: int, total: int) -> str:
    if total == 0:
        return "sin datos"
    ratio = con_evidencia / total
    if ratio == 0:
        return "bajo (autodeclarado)"
    return "medio" if ratio < 0.5 else "alto (respaldado por evidencia)"


# ---------------------------------------------------------------------------
# CAPA 2 — Recomendaciones
# ---------------------------------------------------------------------------

def recomendar(gap_register: list[dict], pais: str | None = "CO") -> list[dict]:
    """Hoja de ruta priorizada por reducción de riesgo vs. esfuerzo, con
    justificación normativa (output 2.3) anclada en los marcos universales
    (ISO 42001, NIST AI RMF y principios éticos UNESCO/OCDE)."""
    data = load_data()
    rec_index = {r["id_control"]: r for r in data["recommendations"]}
    fundamentos = _fundamentos_pais(data, pais)

    salida = []
    for gap in gap_register:
        rec = rec_index.get(gap["id_control"])
        if not rec:  # una brecha sin control de destino no genera recomendación
            continue
        riesgo = _SEVERIDAD_PESO[gap["severidad"]]
        esfuerzo = _ESFUERZO_PESO.get(rec["esfuerzo"], 2)
        salida.append({
            **rec,
            "severidad": gap["severidad"],
            "ejes": gap.get("ejes", []),
            "principios": gap.get("principios", []),
            "prioridad": round(riesgo / esfuerzo, 2),
            "plano": {"x_esfuerzo": esfuerzo, "y_riesgo": riesgo},
            "justificacion": {                       # output 2.3
                "fundamento_pais": fundamentos,
                "principios_eticos": gap.get("principios", []),
                "control_iso": gap["id_control"],
                "funcion_nist": rec.get("nist"),
            },
        })
    salida.sort(key=lambda r: r["prioridad"], reverse=True)
    return salida


def _fundamentos_pais(data: dict, pais: str | None) -> list[str]:
    if not pais:
        return []
    return [c["referencia_legal"] for c in data["corpus"]
            if c.get("pais") == pais and "Constituci" in c.get("fuente", "")]
