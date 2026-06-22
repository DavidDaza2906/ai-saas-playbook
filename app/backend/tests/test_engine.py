"""Tests unitarios del motor determinista (Capa 1 + Capa 2).

Sin LLM, sin Voyage, sin red. Puros y rápidos (<1s).
Verifican reproducibilidad, edge cases y corrección del diagnóstico.

Correr: .venv/bin/pytest tests/test_engine.py -v
"""

from __future__ import annotations

from engine import diagnosticar, recomendar, _puntaje, _valor_tramo, _pesos, load_data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _respuestas_caso_fuerte_etico() -> dict:
    """PYME fuerte en ético (supervisión, consentimiento) pero débil en ISO (sin docs)."""
    return {
        "q1": "no", "q2": ["a"], "q2a": "si", "q3": 2, "q3b": "algunos",
        "q4": ["bajo", "bajo"], "q5": "3", "q5a": "parcial", "q5b": "parcial",
        "q6": "si", "q6a": "si", "q6b": "si", "q6c": "si",
        "q7": ["a"], "q8a": "4", "q8b": ["a"], "q8b_herr": "si",
        "q9b": "no", "q10b": "4", "q11": "no", "q12": "no",
        "q13": "4", "q13_just": "x",
    }


def _respuestas_caso_fuerte_iso() -> dict:
    """PYME fuerte en ISO/docs pero débil en ético (sin supervisión, sin consentimiento)."""
    return {
        "q1": "si", "q2": ["b"], "q2a": "si", "q3": 5, "q3b": "todos",
        "q4": ["alto", "alto", "alto", "alto", "alto"],
        "q5": "5", "q5a": "si", "q5b": "si",
        "q6": "si", "q6a": "no", "q6b": "no", "q6c": "no",
        "q7": ["c"], "q8a": "2", "q8b": ["d"], "q8b_herr": "no",
        "q9b": "si", "q9a": "no", "q9b_doc": "si",
        "q10b": "2", "q10a": "no", "q10b_mon": "x",
        "q11": "si", "q11a": "no", "q11b": "no",
        "q12": "si", "q12a": "no", "q12b": "no",
        "q13": "2", "q13_just": "x",
    }


def _respuestas_todo_implementado() -> dict:
    """Todas las preguntas respondidas con el valor máximo (mejor caso)."""
    return {
        "q1": "si", "q2": ["a"], "q2a": "si", "q3": 5, "q3b": "todos",
        "q4": ["bajo", "bajo", "bajo", "bajo", "bajo"],
        "q5": "5", "q5a": "si", "q5b": "si",
        "q6": "si", "q6a": "si", "q6b": "si", "q6c": "si",
        "q7": ["a"], "q8a": "5", "q8b": ["a"], "q8b_herr": "si",
        "q9b": "si", "q9a": "si", "q9b_doc": "si",
        "q10b": "5", "q10a": "si", "q10b_mon": "gerente",
        "q11": "si", "q11a": "si", "q11b": "si",
        "q12": "si", "q12a": "si", "q12b": "si",
        "q13": "5", "q13_just": "x",
    }


def _respuestas_todo_ausente() -> dict:
    """Todas las preguntas respondidas con el valor mínimo (peor caso)."""
    return {
        "q1": "no", "q2": ["d"], "q3": 1, "q3b": "no",
        "q4": ["alto"], "q5": "1",
        "q6": "si", "q6a": "no", "q6b": "no", "q6c": "no",
        "q7": ["c"], "q8a": "1", "q8b": ["d"], "q8b_herr": "no",
        "q9b": "si", "q9a": "no", "q9b_doc": "no",
        "q10b": "1", "q10a": "no", "q10b_mon": "x",
        "q11": "si", "q11a": "no", "q11b": "no",
        "q12": "si", "q12a": "no", "q12b": "no",
        "q13": "1", "q13_just": "x",
    }


# ---------------------------------------------------------------------------
# Tests de reproducibilidad
# ---------------------------------------------------------------------------

def test_reproducibilidad_mismo_vector():
    """Mismas respuestas → mismo vector (2 llamadas, asserts iguales)."""
    r = _respuestas_caso_fuerte_etico()
    d1 = diagnosticar("3", r)
    d2 = diagnosticar("3", r)
    assert d1["diagnostico_vector"] == d2["diagnostico_vector"]
    assert d1["madurez_nist"] == d2["madurez_nist"]
    assert d1["principios_eticos"] == d2["principios_eticos"]
    assert d1["gap_register"] == d2["gap_register"]


def test_reproducibilidad_mismo_gap_register():
    """Gap register es idempotente: mismo orden, misma longitud."""
    r = _respuestas_caso_fuerte_iso()
    g1 = diagnosticar("3", r)["gap_register"]
    g2 = diagnosticar("3", r)["gap_register"]
    assert [g["id_control"] for g in g1] == [g["id_control"] for g in g2]
    assert [g["severidad"] for g in g1] == [g["severidad"] for g in g2]


# ---------------------------------------------------------------------------
# Tests de casos extremos
# ---------------------------------------------------------------------------

def test_vector_extremo_alto():
    """Todas implementado → vector cerca de 100/100/100."""
    d = diagnosticar("3", _respuestas_todo_implementado())
    v = d["diagnostico_vector"]
    assert v["x_etico"] is not None and v["x_etico"] >= 80, f"x_etico={v['x_etico']}"
    assert v["y_iso"] is not None and v["y_iso"] >= 80, f"y_iso={v['y_iso']}"
    assert v["z_nist"] is not None and v["z_nist"] >= 80, f"z_nist={v['z_nist']}"


def test_vector_extremo_bajo():
    """Todas ausente → vector bajo (<30 en cada eje)."""
    d = diagnosticar("3", _respuestas_todo_ausente())
    v = d["diagnostico_vector"]
    assert v["x_etico"] is not None and v["x_etico"] < 30, f"x_etico={v['x_etico']}"
    assert v["y_iso"] is not None and v["y_iso"] < 30, f"y_iso={v['y_iso']}"
    assert v["z_nist"] is not None and v["z_nist"] < 30, f"z_nist={v['z_nist']}"


def test_vector_discrimina_ejes():
    """Caso fuerte ético → x > y, z; caso fuerte ISO → y > x (los pesos separan ejes)."""
    d_etico = diagnosticar("3", _respuestas_caso_fuerte_etico())
    d_iso = diagnosticar("3", _respuestas_caso_fuerte_iso())
    v_e = d_etico["diagnostico_vector"]
    v_i = d_iso["diagnostico_vector"]
    # los pesos finos deben hacer que los vectores sean distintos
    assert v_e != v_i, "los pesos no discriminan: vectores idénticos"


# ---------------------------------------------------------------------------
# Tests de ramas condicionales
# ---------------------------------------------------------------------------

def test_q3_cero_salta_dependientes():
    """q3=0 → q4/q5/q7/q10b/q11 no aplican (sus condiciones son q3 en [1-3,4+])."""
    r = {"q1": "no", "q3": 0, "q6": "no", "q13": "2", "q13_just": "x"}
    d = diagnosticar("3", r)
    detalle = d["verificabilidad"]["detalle"]
    # q4, q5, q7 no deben estar en respondidas
    for pid in ("q4", "q5", "q7", "q10b", "q11"):
        assert pid not in detalle, f"{pid} debería saltarse cuando q3=0"
    # inventario vacío (sin sistemas)
    assert d["inventario"] == []


def test_subpreguntas_condicionales_activas():
    """q6="si" → q6a/q6b/q6c activas; q6="no" → no."""
    r_si = {"q1": "no", "q3": 2, "q4": ["bajo", "bajo"], "q5": "3",
            "q6": "si", "q6a": "si", "q6b": "si", "q6c": "si",
            "q8a": "3", "q9b": "no", "q10b": "4", "q11": "no",
            "q12": "no", "q13": "3", "q13_just": "x"}
    d_si = diagnosticar("3", r_si)
    detalle_si = d_si["verificabilidad"]["detalle"]
    assert "q6a" in detalle_si
    assert "q6b" in detalle_si
    assert "q6c" in detalle_si

    r_no = dict(r_si)
    r_no["q6"] = "no"
    # quitar subpreguntas de q6
    for k in ("q6a", "q6b", "q6c"):
        r_no.pop(k, None)
    d_no = diagnosticar("3", r_no)
    detalle_no = d_no["verificabilidad"]["detalle"]
    for pid in ("q6a", "q6b", "q6c"):
        assert pid not in detalle_no, f"{pid} no debería activarse cuando q6=no"


def test_ruta_a_sin_modulo_b():
    """Bifurcación 1 (productos terceros) → q9b/q10b no aplican (ramas [2,3])."""
    r = {"q1": "no", "q3": 2, "q4": ["bajo", "bajo"], "q5": "3",
         "q6": "no", "q8a": "3", "q11": "no", "q12": "no",
         "q13": "3", "q13_just": "x"}
    d = diagnosticar("1", r)
    detalle = d["verificabilidad"]["detalle"]
    assert "q9b" not in detalle, "q9b no aplica en ruta A"
    assert "q10b" not in detalle, "q10b no aplica en ruta A"
    # q8a sí aplica (ramas [1,3])
    assert "q8a" in detalle


def test_ruta_b_sin_modulo_a():
    """Bifurcación 2 (procesos internos) → q8a/q8b no aplican (ramas [1,3])."""
    r = {"q1": "no", "q3": 2, "q4": ["bajo", "bajo"], "q5": "3",
         "q6": "no", "q9b": "si", "q9a": "si", "q9b_doc": "si",
         "q10b": "4", "q11": "no", "q12": "no",
         "q13": "3", "q13_just": "x"}
    d = diagnosticar("2", r)
    detalle = d["verificabilidad"]["detalle"]
    assert "q8a" not in detalle, "q8a no aplica en ruta B"
    assert "q8b" not in detalle, "q8b no aplica en ruta B"
    # q9b sí aplica (ramas [2,3])
    assert "q9b" in detalle


# ---------------------------------------------------------------------------
# Tests de tipos de respuesta
# ---------------------------------------------------------------------------

def test_matriz_agregacion_peor():
    """Matriz [bajo, alto] → puntaje = alto (peor caso, no promedio)."""
    data = load_data()
    q4 = next(p for p in data["questions"]["preguntas"] if p["id"] == "q4")
    p = _puntaje(q4, data, ["bajo", "alto"])
    # bajo=1.0, alto=0.0 → peor = 0.0
    assert p == 0.0, f"matriz peor caso debería ser 0.0, got {p}"


def test_matriz_agregacion_todos_bajos():
    """Matriz [bajo, bajo] → puntaje = 1.0 (todos bajos = sin riesgo alto)."""
    data = load_data()
    q4 = next(p for p in data["questions"]["preguntas"] if p["id"] == "q4")
    p = _puntaje(q4, data, ["bajo", "bajo"])
    assert p == 1.0, f"matriz todos bajos debería ser 1.0, got {p}"


def test_numero_tramos():
    """q3 numérico: 0→tramo '0', 2→'1-3', 5→'4+', 'ns'→'ns'."""
    data = load_data()
    q3 = next(p for p in data["questions"]["preguntas"] if p["id"] == "q3")
    assert _valor_tramo(q3, 0) == "0"
    assert _valor_tramo(q3, 2) == "1-3"
    assert _valor_tramo(q3, 5) == "4+"
    assert _valor_tramo(q3, "ns") == "ns"


def test_numero_puntaje_tramos():
    """q3: 0→None (no puntúa), 2→0.5, 5→1.0."""
    data = load_data()
    q3 = next(p for p in data["questions"]["preguntas"] if p["id"] == "q3")
    assert _puntaje(q3, data, 0) is None
    assert _puntaje(q3, data, 2) == 0.5
    assert _puntaje(q3, data, 5) == 1.0


# ---------------------------------------------------------------------------
# Tests de verificabilidad y gap register
# ---------------------------------------------------------------------------

def test_verificabilidad_niveles():
    """0 evidencias → 'bajo'; algunas → 'medio' o 'alto'."""
    r = {"q1": "no", "q3": 2, "q4": ["bajo", "bajo"], "q5": "3",
         "q6": "no", "q8a": "3", "q11": "no", "q12": "no",
         "q13": "3", "q13_just": "x"}
    d_bajo = diagnosticar("1", r, evidencias=[])
    assert "bajo" in d_bajo["verificabilidad"]["nivel"]

    # con evidencia en todas las respondidas → alto
    respondidas = list(d_bajo["verificabilidad"]["detalle"].keys())
    d_alto = diagnosticar("1", r, evidencias=respondidas)
    assert "alto" in d_alto["verificabilidad"]["nivel"]


def test_gap_register_ordenado_severidad():
    """Gap register ordenado: brechas altas antes que medias, medias antes que bajas."""
    r = _respuestas_caso_fuerte_iso()
    d = diagnosticar("3", r)
    severidades = [g["severidad"] for g in d["gap_register"]]
    # verificar que está ordenado de mayor a menor peso
    pesos = {"alta": 3, "media": 2, "baja": 1}
    pesos_seq = [pesos[s] for s in severidades]
    assert pesos_seq == sorted(pesos_seq, reverse=True), \
        f"gap_register no ordenado por severidad: {severidades}"


def test_texto_abierto_no_puntua():
    """Pregunta tipo texto no afecta el vector ni entra en respondidas."""
    r = {"q1": "no", "q3": 2, "q4": ["bajo", "bajo"], "q5": "3",
         "q6": "no", "q7": ["c"], "q8a": "3", "q10b": "2",
         "q11": "no", "q12": "no", "q13": "3", "q13_just": "mi justificación"}
    d = diagnosticar("1", r)
    # q13_just es tipo texto, no debe estar en respondidas
    assert "q13_just" not in d["verificabilidad"]["detalle"]
    # pero debe estar en texto_abierto
    assert d["texto_abierto"].get("q13_just") == "mi justificación"


def test_mapeo_a_tres_ejes():
    """Pregunta con nist+iso+principio aporta a los 3 ejes (pesos binarios)."""
    data = load_data()
    # q6 tiene nist=[MAP,GOVERN], iso=[A.6.2], principio=[autonomia,justicia]
    q6 = next(p for p in data["questions"]["preguntas"] if p["id"] == "q6")
    pesos = _pesos(q6)
    assert pesos["etico"] > 0, "q6 debería aportar al eje ético"
    assert pesos["iso"] > 0, "q6 debería aportar al eje ISO"
    assert pesos["nist"] > 0, "q6 debería aportar al eje NIST"


# ---------------------------------------------------------------------------
# Tests de Capa 2 (recomendaciones)
# ---------------------------------------------------------------------------

def test_recomendaciones_priorizadas():
    """Recomendaciones ordenadas por prioridad (mayor primero)."""
    r = _respuestas_caso_fuerte_iso()
    d = diagnosticar("3", r)
    recs = recomendar(d["gap_register"], pais="CO")
    assert len(recs) > 0
    prioridades = [r["prioridad"] for r in recs]
    assert prioridades == sorted(prioridades, reverse=True), \
        f"recomendaciones no ordenadas: {prioridades}"


def test_recomendaciones_tienen_justificacion():
    """Cada recomendación incluye justificación normativa (output 2.3)."""
    r = _respuestas_caso_fuerte_iso()
    d = diagnosticar("3", r)
    recs = recomendar(d["gap_register"], pais="CO")
    for rec in recs:
        assert "justificacion" in rec
        assert rec["justificacion"]["control_iso"]
        assert rec["justificacion"]["funcion_nist"]


def test_brecha_sin_rec_no_genera_recomendacion():
    """Una brecha sin entrada en recommendations.json no genera recomendación (§147)."""
    # crear un gap_register con un control inexistente en recommendations
    gap_fake = [{"id_control": "X.99.9", "nombre": "fake", "estado": "ausente",
                 "severidad": "alta", "ejes": ["ISO"], "principios": []}]
    recs = recomendar(gap_fake, pais="CO")
    assert len(recs) == 0, "brecha sin control de destino no debería generar rec"


# ---------------------------------------------------------------------------
# Tests de regresión — bug "todo no" no infla madurez
# ---------------------------------------------------------------------------

def test_todo_no_no_infla_madurez():
    """Bug fix: responder 'no' a todo + q3=0 → MANAGE/MEASURE no son 100.

    Antes, q6/q9b/q11/q12 daban puntaje 1.0 por 'no' (confundían exposición
    con madurez). Si solo q12 puntuaba para MANAGE, el promedio de 1 elemento
    daba 100%. Ahora 'no'=null (sin datos) y se exige mínimo 2 preguntas.
    """
    r = {"q1": "no", "q2": ["d"], "q3": 0, "q6": "no",
         "q12": "no", "q13": "1", "q13_just": "x"}
    d = diagnosticar("3", r)
    m = d["madurez_nist"]
    assert m["MANAGE"] != 100, f"MANAGE no debería ser 100 con todo 'no', got {m['MANAGE']}"
    assert m["MEASURE"] != 100, f"MEASURE no debería ser 100 con todo 'no', got {m['MEASURE']}"
    assert m["MAP"] != 100, f"MAP no debería ser 100 con todo 'no', got {m['MAP']}"


def test_funcion_sin_datos_suficientes_null():
    """Si una función NIST tiene <2 preguntas puntuadas → null (sin datos suficientes)."""
    r = {"q1": "no", "q2": ["d"], "q3": 0, "q6": "no",
         "q12": "no", "q13": "1", "q13_just": "x"}
    d = diagnosticar("3", r)
    # MANAGE solo tenía q12 (que ahora da null con 'no') → 0 preguntas puntuadas → null
    assert d["madurez_nist"]["MANAGE"] is None, \
        f"MANAGE debería ser null con <2 preguntas puntuadas, got {d['madurez_nist']['MANAGE']}"


def test_todo_no_vector_no_celebra():
    """Caso todo 'no' + q3=0: el vector no debe reportar madurez alta en ningún eje."""
    r = {"q1": "no", "q2": ["d"], "q3": 0, "q6": "no",
         "q12": "no", "q13": "1", "q13_just": "x"}
    d = diagnosticar("3", r)
    v = d["diagnostico_vector"]
    # ningún eje debe ser >= 80 (falsa madurez)
    for eje, val in v.items():
        if val is not None:
            assert val < 80, f"{eje}={val} es falsa madurez para todo 'no'"


def test_poc_normal_sigue_funcionando():
    """El fix no rompe el caso POC normal — el vector sigue discriminando."""
    r = {
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
    }
    d = diagnosticar("3", r, evidencias=["q1"])
    v = d["diagnostico_vector"]
    # el vector debe tener valores no nulos en los 3 ejes (hay suficientes preguntas)
    assert v["x_etico"] is not None
    assert v["y_iso"] is not None
    assert v["z_nist"] is not None
    # y no deben ser 100 (hay brechas)
    assert v["x_etico"] < 100
    assert v["y_iso"] < 100
    assert v["z_nist"] < 100
    # hay gaps
    assert len(d["gap_register"]) > 0
