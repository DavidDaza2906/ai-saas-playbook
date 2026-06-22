"""
Validador del árbol de preguntas contra el contrato (data/SCHEMA_PREGUNTAS.md).

Úsalo tras cargar las preguntas reales:
    .venv/bin/python validate_questions.py
Sale con código 1 si hay errores. Avisa (no bloquea) si se supera el tope de 20.
"""

import sys

from engine import FUNCIONES_NIST, PRINCIPIOS, load_data

TIPOS_VALIDOS = {"multiple", "multiple_seleccion", "likert", "numero", "matriz",
                 "texto", "estado"}


def _check_pregunta(p: dict, ids: set[str], iso_validos: set[str],
                    errores: list[str], avisos: list[str], path: str,
                    es_sub: bool = False) -> None:
    """Valida una pregunta (base o subpregunta). `path` = "q3" o "q3 > q3a"."""
    pid = p.get("id", "??")
    loc = f"{path} ({pid})"

    for campo in ("id", "texto", "contexto_pyme"):
        if not p.get(campo):
            errores.append(f"{loc}: falta el campo obligatorio '{campo}'.")
    # 'ramas' es obligatorio en base; en subpreguntas se hereda si falta
    if not es_sub and not p.get("ramas"):
        errores.append(f"{loc}: falta el campo obligatorio 'ramas'.")
    elif es_sub and not p.get("ramas") and not p.get("condicion"):
        avisos.append(f"{loc}: subpregunta sin 'ramas' ni 'condicion'; se hereda del padre.")

    tipo = p.get("tipo", "estado")
    if tipo not in TIPOS_VALIDOS:
        errores.append(f"{loc}: tipo '{tipo}' inválido. Válidos: {sorted(TIPOS_VALIDOS)}.")

    # mapeo obligatorio salvo para tipo texto
    mapeo = p.get("mapeo", {})
    if tipo != "texto":
        if not mapeo:
            errores.append(f"{loc}: falta 'mapeo' (obligatorio salvo tipo texto).")
        nist, iso, princ = mapeo.get("nist", []), mapeo.get("iso", []), mapeo.get("principio", [])
        if not nist and not iso:
            errores.append(f"{loc}: debe mapear a ≥1 función NIST o ≥1 control ISO.")
        for f in nist:
            if f.split("-")[0].split(".")[0] not in FUNCIONES_NIST:
                errores.append(f"{loc}: función NIST '{f}' inválida.")
        for c in iso:
            if c not in iso_validos:
                errores.append(f"{loc}: control ISO '{c}' no existe en controls.json.")
        for pr in princ:
            if pr not in PRINCIPIOS:
                errores.append(f"{loc}: principio '{pr}' inválido.")

    # validación por tipo
    if tipo in ("multiple", "multiple_seleccion", "likert", "estado"):
        opts = p.get("opciones")
        if opts is None and tipo != "estado":
            errores.append(f"{loc}: tipo '{tipo}' requiere 'opciones'.")
        elif opts is not None:
            for o in opts:
                if "valor" not in o or "puntaje" not in o:
                    errores.append(f"{loc}: cada opción debe tener 'valor' y 'puntaje' (puede ser null).")
                    break
            if not any(o.get("puntaje") is not None for o in opts):
                errores.append(f"{loc}: ninguna opción puntúa (todas null); la pregunta nunca aportará madurez.")

    elif tipo == "numero":
        tramos = p.get("tramos")
        if not tramos:
            errores.append(f"{loc}: tipo 'numero' requiere 'tramos'.")
        else:
            for t in tramos:
                if "valor_tramo" not in t or "puntaje" not in t:
                    errores.append(f"{loc}: cada tramo debe tener 'valor_tramo' y 'puntaje'.")
                    break
            if not any(t.get("hasta") is None for t in tramos):
                avisos.append(f"{loc}: ningún tramo con 'hasta: null' (no hay destino para 'No sé').")

    elif tipo == "matriz":
        if not p.get("opciones"):
            errores.append(f"{loc}: tipo 'matriz' requiere 'opciones'.")
        if not p.get("filas_de"):
            errores.append(f"{loc}: tipo 'matriz' requiere 'filas_de' (ID de pregunta 'numero').")
        elif p["filas_de"] not in ids:
            errores.append(f"{loc}: 'filas_de' apunta a pregunta inexistente '{p['filas_de']}'.")
        agg = p.get("agregacion", "peor")
        if agg not in ("peor", "promedio"):
            errores.append(f"{loc}: agregacion '{agg}' inválida (peor|promedio).")

    # condición debe apuntar a una pregunta existente
    cond = p.get("condicion")
    for c in (cond if isinstance(cond, list) else [cond] if cond else []):
        if c.get("pregunta") not in ids:
            errores.append(f"{loc}: condicion apunta a pregunta inexistente '{c.get('pregunta')}'.")

    # subpreguntas (recursión)
    subs = p.get("subpreguntas", [])
    if len(subs) > 20:
        errores.append(f"{loc}: demasiadas subpreguntas (máx 20).")
    for sub in subs:
        _check_pregunta(sub, ids, iso_validos, errores, avisos, f"{path} > {sub.get('id','??')}", es_sub=True)


def main() -> int:
    data = load_data()
    q = data["questions"]
    iso_validos = {c["id"] for c in data["controls"]["iso_controls"]}
    errores, avisos = [], []

    preguntas = q.get("preguntas", [])
    # Recoger todos los IDs (base + subpreguntas) para validar condiciones y duplicados
    todos_ids = []

    def _recoger(ps):
        for p in ps:
            todos_ids.append(p.get("id"))
            _recoger(p.get("subpreguntas", []))
    _recoger(preguntas)

    ids_set = set(todos_ids)
    base_count = len(preguntas)
    total_count = len(todos_ids)

    if base_count > 20:
        avisos.append(f"Hay {base_count} preguntas base (PROPUESTAFINAL §127 recomienda ≤20).")
    if len(todos_ids) != len(ids_set):
        from collections import Counter
        dups = [k for k, v in Counter(todos_ids).items() if v > 1]
        errores.append(f"IDs duplicados en el árbol (base + subpreguntas): {dups}.")

    principios_cubiertos = set()

    def _cubrir(p):
        for pr in p.get("mapeo", {}).get("principio", []):
            if pr in PRINCIPIOS:
                principios_cubiertos.add(pr)
        for sub in p.get("subpreguntas", []):
            _cubrir(sub)
    for p in preguntas:
        _cubrir(p)

    for p in preguntas:
        _check_pregunta(p, ids_set, iso_validos, errores, avisos, p.get("id", "??"))

    faltantes = set(PRINCIPIOS) - principios_cubiertos
    if faltantes:
        avisos.append(f"Principios sin ninguna pregunta (saldrán null): {', '.join(sorted(faltantes))}.")

    print(f"Preguntas base: {base_count} | Total (con subpreguntas): {total_count}")
    for a in avisos:
        print("  AVISO:", a)
    if errores:
        for e in errores:
            print("  ERROR:", e)
        print(f"\n{len(errores)} error(es). El árbol NO cumple el contrato.")
        return 1
    print("\nOK: el árbol cumple el contrato de esquema.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
