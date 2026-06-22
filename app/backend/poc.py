"""Caso de prueba de concepto (alineado a ARBOL_PREGUNTAS.md).

PYME ruta C (productos de IA para terceros + procesos internos) con 3 sistemas,
uno de alto riesgo (preselección de hojas de vida), datos personales sin
consentimiento documentado, sin supervisión humana.

Recorre el núcleo determinista (Capa 1 + Capa 2) sin LLM ni red.
Ejecutar: .venv/bin/python poc.py
"""

import json

from engine import diagnosticar, recomendar

# Ruta C: ambas (productos para terceros + procesos internos)
CASO = {
    "bifurcacion": "3",
    "respuestas": {
        "q1": "parcial",          # políticas parciales
        "q2": ["c"],              # responsabilidad en gerencia general
        "q2a": "parcial",         # acceso a info parcial
        "q3": 3,                  # 3 sistemas de IA (tipo numero)
        "q3b": "algunos",         # sabe cómo decide algunos
        "q4": ["medio", "alto", "bajo"],  # matriz: uno alto, uno medio, uno bajo
        "q5": "2",                # documentación muy limitada
        "q5a": "parcial",         # acceso a doc del proveedor parcial
        "q5b": "no",              # no sabe qué datos usa
        "q6": "si",               # usa datos personales
        "q6a": "no",              # sin consentimiento documentado
        "q6b": "no",              # sin DPIA
        "q6c": "no",              # sin responsable de datos
        "q7": ["c"],              # decisiones automáticas sin revisión humana
        "q7a": "nadie",           # texto: quién monitorea
        "q7b": "nunca",           # frecuencia de revisión
        "q8a": "2",               # comunicación confusa sobre IA
        "q8a_just": "temor a perder clientes",
        "q8b": ["d"],             # no evalúa sesgo y no ve por qué
        "q8b_herr": "no",         # sin herramientas de auditoría
        "q9b": "si",              # usa IA con datos de empleados
        "q9a": "no",              # empleados no informados
        "q9b_doc": "no",          # sin documentación de datos
        "q10b": "2",              # dependencia alta
        "q10a": "no",             # sin plan de contingencia
        "q10b_mon": "nadie",      # texto: quién monitorea
        "q11": "si",              # hizo cambios en 12 meses
        "q11a": "no",             # sin re-evaluación
        "q11b": "no",             # no comunicó cambios
        "q12": "si",              # tuvo incidente
        "q12a": "no",             # no documentado
        "q12b": "no",             # sin acciones correctivas
        "q13": "3",               # autoevaluación media
        "q13_just": "creemos que estamos bien pero no sabemos bien qué hacer"
    },
    "evidencias": ["q1"],  # subió políticas parciales como evidencia
}


def main():
    diag = diagnosticar(CASO["bifurcacion"], CASO["respuestas"], CASO["evidencias"])
    recs = recomendar(diag["gap_register"])

    print("=" * 60)
    print("CAPA 1 — DIAGNÓSTICO (caso POC del árbol real)")
    print("=" * 60)
    v = diag["diagnostico_vector"]
    print("Perfil:", diag["perfil"]["descripcion"])
    print(f"\nVECTOR DE DIAGNÓSTICO (x,y,z) = ÉTICO {v['x_etico']} · ISO {v['y_iso']} · NIST {v['z_nist']}")
    print("\nMadurez NIST:", diag["madurez_nist"])
    print("Eje ético (principios UNESCO/OCDE):", diag["principios_eticos"])
    print("\nInventario de casos de uso:")
    for it in diag["inventario"]:
        print(f"  - {it['caso']} (riesgo {it['riesgo']})")
    print("\nGap register (priorizado):")
    for g in diag["gap_register"]:
        print(f"  [{g['severidad'].upper():5}] {g['id_control']:7} {g['nombre']} ({', '.join(g['ejes'])})")
    print(f"\nVerificabilidad: {diag['verificabilidad']['nivel']} "
          f"({diag['verificabilidad']['con_evidencia']}/{diag['verificabilidad']['respondidas']} con evidencia)")
    print(f"Respondidas: {diag['verificabilidad']['respondidas']} preguntas")
    if diag["texto_abierto"]:
        print(f"Texto abierto capturado en: {list(diag['texto_abierto'].keys())}")

    print("\n" + "=" * 60)
    print("CAPA 2 — RECOMENDACIONES (priorizadas riesgo/esfuerzo)")
    print("=" * 60)
    for r in recs:
        print(f"\n[prioridad {r['prioridad']}] {r['id_control']} — {r['brecha']}")
        print(f"  → {r['recomendacion']}")
        print(f"  NIST {r['nist']} | esfuerzo {r['esfuerzo']} | fase {r['fase']} | rol {r['rol']}")
        print(f"  Cierre: {r['criterio_cierre']}")


if __name__ == "__main__":
    main()
