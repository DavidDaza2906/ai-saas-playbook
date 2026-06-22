"""
Mini-harness de evaluación RAGAS — métricas para el paper.

Corre sobre un golden set (data/golden_set.json) y mide:
  - **Recall@k** (retrieval): de los chunks esperados, cuántos aparecen en el top-k.
  - **Precisión de citas** (verificación): % de citas en la política que existen
    en el corpus (citas válidas / total citas). Guardrail anti-alucinación.
  - **Faithfulness** (LLM-as-judge): % de afirmaciones de la política respaldadas
    por las fuentes (faithful / total). 3ª capa anti-alucinación.

Paraleliza la generación de políticas + faithfulness con ThreadPoolExecutor para
no esperar secuencialmente (~15 min → ~2-3 min con 10 workers).

Uso:
    .venv/bin/python eval_harness.py                          # solo retrieval + recall (rápido)
    .venv/bin/python eval_harness.py --con-faithfulness       # + política + faithfulness (paralelo)
    .venv/bin/python eval_harness.py --k 5                    # top-k para recall (default 6)
    .venv/bin/python eval_harness.py --report                 # escribe reporte markdown
    .venv/bin/python eval_harness.py --model kimi-k2.6        # modelo LLM (default kimi-k2.6)
    .venv/bin/python eval_harness.py --workers 10             # concurrencia (default 10)

Salida: tabla por consulta + agregados (medias) + JSON con detalle.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from rag import retriever, llm_client, faithfulness
from rag.generator import generar_politica
from rag.verifier import validar
from engine import load_data

GOLDEN = Path(__file__).parent / "data" / "golden_set.json"
OUT_JSON = Path(__file__).parent / "data" / "eval_result.json"
OUT_MD = Path(__file__).parent / "data" / "eval_report.md"

MODELO_DEFAULT = "kimi-k2.6"  # modelo para el harness (no afecta la API del SaaS)


def _recall_at_k(recuperadas: list[str], esperadas: list[str], k: int) -> float:
    """Proporción de referencias esperadas que aparecen en el top-k de las recuperadas."""
    if not esperadas:
        return 1.0
    top_k = recuperadas[:k]
    hits = sum(1 for ref in esperadas if any(ref in c for c in top_k))
    return hits / len(esperadas)


def _precision_citas(texto: str, fuentes: list[dict]) -> float:
    """% de citas en el texto que existen en el corpus/fuentes."""
    ver = validar(texto, fuentes)
    total = len(ver.get("validas", [])) + len(ver.get("invalidas", []))
    if total == 0:
        return 1.0  # sin citas = nada que invalidar
    return len(ver.get("validas", [])) / total


def _procesar_una(g: dict, k: int, con_faithfulness: bool, modelo: str) -> dict:
    """Procesa una consulta del golden set: retrieval + política (+ faithfulness).
    Diseñada para correr en paralelo (sin estado compartido)."""
    t0 = time.time()
    rec = retriever.retrieve(g["query"], filtro=g["filtros"], top_k=k, pais="CO")
    if rec["abstain"]:
        return {"id": g["id"], "tema": g["tema"], "abstain": True,
                "politica_modo": "abstain"}

    # recall
    recuperadas = [c.get("referencia_legal", c.get("referencia", "")) for c in rec["chunks"]]
    recall = _recall_at_k(recuperadas, g["esperado_referencias"], k)
    iso_hits = [c.get("id_control") for c in rec["chunks"] if c.get("id_control")]
    iso_encontrados = set(g["esperado_iso"]) & set(iso_hits)

    # política
    brechas = [{"id_control": iso, "brecha": g["tema"], "nombre": g["tema"], "nist": "GOVERN"}
               for iso in g["esperado_iso"]]
    pol = generar_politica({"descripcion": "PYME", "sector": "general"}, brechas,
                           rec["chunks"], model=modelo)
    prec_citas = _precision_citas(pol["texto"], rec["chunks"])

    entry = {
        "id": g["id"], "tema": g["tema"], "abstain": False,
        "n_chunks": len(rec["chunks"]),
        "recall_at_k": round(recall, 3),
        "iso_esperados_encontrados": sorted(iso_encontrados),
        "iso_esperados_total": g["esperado_iso"],
        "referencias_recuperadas": recuperadas,
        "politica_modo": pol["modo"], "politica_chars": len(pol["texto"]),
        "precision_citas": round(prec_citas, 3),
        "tiempo_politica_s": round(time.time() - t0, 1),
    }

    if con_faithfulness and pol["modo"] == "llm" and llm_client.disponible():
        t1 = time.time()
        # faithfulness usa glm-5.2 (fiable para JSON); no el modelo de política
        f = faithfulness.verificar(pol["texto"], rec["chunks"], model="glm-5.2")
        entry["faithfulness"] = {
            "modo": f["modo"],
            "n_claims": f["n_claims"],
            "score": f["score"],
            "n_faithful": f["n_faithful"],
            "n_unfaithful": f["n_unfaithful"],
            "n_partial": f["n_partial"],
            "global_faithful": f["faithful"],
        }
        entry["tiempo_faithfulness_s"] = round(time.time() - t1, 1)
    return entry


def evaluar_retrieval(k: int = 6) -> list[dict]:
    """Evalúa retrieval + recall sobre el golden set (sin LLM para política)."""
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    resultados = []
    for g in golden:
        rec = retriever.retrieve(g["query"], filtro=g["filtros"], top_k=k, pais="CO")
        recuperadas = [c.get("referencia_legal", c.get("referencia", "")) for c in rec["chunks"]]
        recall = _recall_at_k(recuperadas, g["esperado_referencias"], k)
        iso_hits = [c.get("id_control") for c in rec["chunks"] if c.get("id_control")]
        iso_encontrados = set(g["esperado_iso"]) & set(iso_hits)
        resultados.append({
            "id": g["id"], "tema": g["tema"], "abstain": rec["abstain"],
            "n_chunks": len(rec["chunks"]),
            "recall_at_k": round(recall, 3),
            "iso_esperados_encontrados": sorted(iso_encontrados),
            "iso_esperados_total": g["esperado_iso"],
            "referencias_recuperadas": recuperadas,
        })
    return resultados


def evaluar_con_politicas(k: int = 6, con_faithfulness: bool = False,
                          modelo: str = MODELO_DEFAULT, workers: int = 10) -> list[dict]:
    """Evalúa retrieval + generación + citas (+ faithfulness opcional) en paralelo."""
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    resultados = [None] * len(golden)
    t_total = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futuros = {
            pool.submit(_procesar_una, g, k, con_faithfulness, modelo): i
            for i, g in enumerate(golden)
        }
        for fut in as_completed(futuros):
            i = futuros[fut]
            try:
                entry = fut.result()
            except Exception as e:
                entry = {"id": golden[i]["id"], "tema": golden[i]["tema"],
                         "error": str(e)[:200]}
            resultados[i] = entry
            print(f"  [{sum(1 for r in resultados if r)}/{len(golden)}] "
                  f"{entry.get('id','?')} {entry.get('tema','?')}: "
                  f"recall={entry.get('recall_at_k','—')} "
                  f"prec_citas={entry.get('precision_citas','—')} "
                  f"faith={entry.get('faithfulness',{}).get('score','—')}")
    print(f"  Tiempo total: {time.time() - t_total:.1f}s ({workers} workers, modelo {modelo})")
    return resultados


def _agregados(retrieval: list[dict], politicas: list[dict] | None) -> dict:
    agg = {}
    recalls = [r["recall_at_k"] for r in retrieval if not r.get("abstain")]
    agg["recall_at_k_media"] = round(statistics.mean(recalls), 3) if recalls else None
    agg["recall_at_k_min"] = round(min(recalls), 3) if recalls else None
    agg["recall_at_k_max"] = round(max(recalls), 3) if recalls else None
    agg["n_abstain_retrieval"] = sum(1 for r in retrieval if r.get("abstain"))

    if politicas:
        precs = [p["precision_citas"] for p in politicas if "precision_citas" in p]
        agg["precision_citas_media"] = round(statistics.mean(precs), 3) if precs else None
        agg["n_politicas_llm"] = sum(1 for p in politicas if p.get("politica_modo") == "llm")
        agg["n_abstain_politica"] = sum(1 for p in politicas if p.get("abstain"))
        faiths = [p["faithfulness"]["score"] for p in politicas
                  if "faithfulness" in p and p["faithfulness"].get("score") is not None]
        if faiths:
            agg["faithfulness_score_media"] = round(statistics.mean(faiths), 3)
            agg["faithfulness_score_min"] = round(min(faiths), 3)
            agg["n_unfaithful_total"] = sum(p["faithfulness"]["n_unfaithful"]
                                            for p in politicas if "faithfulness" in p)
    return agg


def _escribir_reporte(retrieval: list[dict], politicas: list[dict] | None, agg: dict,
                      con_faith: bool, k: int) -> None:
    lines = [
        "# Reporte de evaluación RAG — métricas para el paper",
        f"> Generado: {time.strftime('%Y-%m-%d %H:%M:%S')} | k={k} | faithfulness={'sí' if con_faith else 'no'}",
        "",
        "## Resumen (agregados)",
        "",
        f"- **Recall@{k} (retrieval):** media {agg.get('recall_at_k_media')} "
        f"(min {agg.get('recall_at_k_min')}, max {agg.get('recall_at_k_max')})",
        f"- **Abstención del retriever:** {agg.get('n_abstain_retrieval')} consultas",
    ]
    if politicas:
        lines += [
            f"- **Precisión de citas:** media {agg.get('precision_citas_media')}",
            f"- **Políticas generadas con LLM:** {agg.get('n_politicas_llm')}",
            f"- **Abstención de política:** {agg.get('n_abstain_politica')}",
        ]
        if agg.get("faithfulness_score_media") is not None:
            lines += [
                f"- **Faithfulness (LLM-as-judge):** media {agg.get('faithfulness_score_media')} "
                f"(min {agg.get('faithfulness_score_min')})",
                f"- **Afirmaciones no respaldadas (unfaithful) total:** {agg.get('n_unfaithful_total')}",
            ]
    lines += ["", "## Las tres capas de defensa anti-alucinación", "",
              "1. **Retrieval con umbral** → abstención si no hay fundamento",
              "2. **Generación citada + validación determinista** → citas contra el índice",
              "3. **Verificador de faithfulness (LLM-as-judge)** → entailment de cada afirmación",
              "", "## Detalle por consulta", "",
              "| ID | Tema | Recall@k | Prec. citas | Faithfulness | Modo |",
              "|---|---|---|---|---|---|"]
    for r in retrieval:
        p = next((x for x in (politicas or []) if x["id"] == r["id"]), {})
        faith = p.get("faithfulness", {}).get("score", "—") if p else "—"
        lines.append(f"| {r['id']} | {r['tema']} | {r['recall_at_k']} | "
                     f"{p.get('precision_citas', '—')} | {faith} | {p.get('politica_modo', '—')} |")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReporte markdown: {OUT_MD}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--con-faithfulness", action="store_true",
                    help="Also run faithfulness LLM-as-judge (parallel).")
    ap.add_argument("--k", type=int, default=6, help="top-k for recall (default 6).")
    ap.add_argument("--report", action="store_true",
                    help="Write markdown report to data/eval_report.md.")
    ap.add_argument("--model", default=MODELO_DEFAULT,
                    help=f"LLM model for policy+faithfulness (default {MODELO_DEFAULT}).")
    ap.add_argument("--workers", type=int, default=10,
                    help="Concurrent workers (default 10).")
    args = ap.parse_args()

    # reset caches para que lea env vars frescas
    retriever._voyage_client.cache_clear()
    retriever._corpus_embeddings.cache_clear()

    print(f"=== Evaluación RAG (k={args.k}, modelo={args.model}, "
          f"workers={args.workers}, faithfulness={args.con_faithfulness}) ===\n")
    print("--- Retrieval + recall (secuencial, respeta rate-limit Voyage) ---")
    retrieval = evaluar_retrieval(k=args.k)
    for r in retrieval:
        print(f"  {r['id']} {r['tema']}: recall@{args.k}={r['recall_at_k']} | "
              f"ISO {r['iso_esperados_encontrados']}/{r['iso_esperados_total']}")

    politicas = None
    if args.con_faithfulness or args.report:
        print(f"\n--- Generación + citas + faithfulness (paralelo, {args.workers} workers) ---")
        politicas = evaluar_con_politicas(k=args.k, con_faithfulness=args.con_faithfulness,
                                          modelo=args.model, workers=args.workers)

    agg = _agregados(retrieval, politicas)
    print("\n=== Agregados ===")
    for k2, v in agg.items():
        print(f"  {k2}: {v}")

    resultado = {"k": args.k, "modelo": args.model, "con_faithfulness": args.con_faithfulness,
                 "retrieval": retrieval, "politicas": politicas, "agregados": agg,
                 "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S')}
    OUT_JSON.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDetalle JSON: {OUT_JSON}")

    if args.report:
        _escribir_reporte(retrieval, politicas, agg, args.con_faithfulness, args.k)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
