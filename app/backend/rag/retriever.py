"""
Retrieval híbrido para el RAG normativo.

Tres rutas combinadas (ver RAG.md §3):
  1. Estructurada: filtro por id_control / funcion_nist (determinista, espinazo).
  2. Densa: embeddings Voyage (semántica, español<->inglés).
  3. Léxica: BM25 (identificadores y siglas exactas).

Fusión por Reciprocal Rank Fusion (RRF) + reranking opcional (Voyage rerank).
Umbral de abstención: si nada supera el score mínimo, se devuelve vacío y el
sistema se abstiene en vez de inventar.

Degrada con elegancia: sin VOYAGE_API_KEY usa estructurada + BM25 (RAG real,
sin dependencia de red).
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from rank_bm25 import BM25Okapi

from engine import load_data

RRF_K = 60
RETRIEVAL_THRESHOLD = float(os.getenv("RETRIEVAL_THRESHOLD", "0.35"))
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
EMB_CACHE_FILE = CACHE_DIR / "embeddings.json"


def _norm(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9.]+", text)


@lru_cache(maxsize=1)
def _bm25():
    corpus = load_data()["corpus"]
    tokens = [_norm(c["texto"] + " " + c["referencia"]) for c in corpus]
    return BM25Okapi(tokens), corpus


@lru_cache(maxsize=1)
def _voyage_client():
    key = os.getenv("VOYAGE_API_KEY")
    if not key:
        return None
    import voyageai
    return voyageai.Client(api_key=key)


@lru_cache(maxsize=1)
def _corpus_embeddings():
    """Embebe el corpus una vez y cachea en disco (data/cache/embeddings.json).
    Así solo se llama a Voyage una vez en la vida del proyecto, no por sesión.
    Devuelve None si no hay key o falla (degrada a BM25+estructurado)."""
    client = _voyage_client()
    if client is None:
        return None
    corpus = load_data()["corpus"]
    model = os.getenv("VOYAGE_EMBED_MODEL", "voyage-3")
    # clave de cache: hash del corpus + modelo
    clave = f"n={len(corpus)}|model={model}|{sum(len(c.get('texto','')) for c in corpus)}"
    if EMB_CACHE_FILE.exists():
        try:
            cached = json.loads(EMB_CACHE_FILE.read_text(encoding="utf-8"))
            if cached.get("clave") == clave and len(cached.get("embeddings", [])) == len(corpus):
                return cached["embeddings"]
        except Exception:
            pass
    # embeber en lotes (Voyage admite listas; lote pequeño para no chocar con límites)
    texts = [c["texto"] for c in corpus]
    all_embs = []
    BATCH = 50
    try:
        for i in range(0, len(texts), BATCH):
            resp = client.embed(texts[i:i + BATCH], model=model, input_type="document")
            all_embs.extend(resp.embeddings)
    except Exception as e:
        print(f"[retriever] Voyage embed falló ({type(e).__name__}); degradando a BM25+estructurado.")
        return None
    # guardar cache
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        EMB_CACHE_FILE.write_text(json.dumps(
            {"clave": clave, "embeddings": all_embs}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    return all_embs


def _cosine(a, b):
    import numpy as np
    a, b = np.array(a), np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def _structured(filtro: dict) -> list[int]:
    """Índices del corpus que casan por id_control o funcion_nist (espinazo)."""
    corpus = load_data()["corpus"]
    ids_control = set(filtro.get("iso", []))
    funcs = set(filtro.get("nist", []))
    hits = []
    for i, c in enumerate(corpus):
        if c.get("id_control") in ids_control or c.get("funcion_nist") in funcs:
            hits.append(i)
    return hits


def _dense_rank(query: str) -> list[int]:
    embs = _corpus_embeddings()
    if embs is None:
        return []
    client = _voyage_client()
    model = os.getenv("VOYAGE_EMBED_MODEL", "voyage-3")
    try:
        q = client.embed([query], model=model, input_type="query").embeddings[0]
    except Exception as e:
        print(f"[retriever] Voyage query-embed falló ({type(e).__name__}); saltando capa densa.")
        return []
    scored = sorted(range(len(embs)), key=lambda i: _cosine(q, embs[i]), reverse=True)
    return scored


def _bm25_rank(query: str) -> list[int]:
    bm25, corpus = _bm25()
    scores = bm25.get_scores(_norm(query))
    return sorted(range(len(corpus)), key=lambda i: scores[i], reverse=True)


def _rrf(rankings: list[list[int]]) -> dict[int, float]:
    fused: dict[int, float] = {}
    for ranking in rankings:
        for rank, idx in enumerate(ranking):
            fused[idx] = fused.get(idx, 0.0) + 1.0 / (RRF_K + rank + 1)
    return fused


def _rerank(query: str, indices: list[int], top_k: int) -> list[tuple[int, float]]:
    """Reranking con Voyage rerank si hay key; si no o falla, mantiene el orden RRF."""
    corpus = load_data()["corpus"]
    client = _voyage_client()
    if client is None:
        return [(i, 1.0) for i in indices[:top_k]]
    model = os.getenv("VOYAGE_RERANK_MODEL", "rerank-2")
    docs = [corpus[i]["texto"] for i in indices]
    try:
        res = client.rerank(query, docs, model=model, top_k=top_k)
        return [(indices[r.index], r.relevance_score) for r in res.results]
    except Exception as e:
        print(f"[retriever] Voyage rerank falló ({type(e).__name__}); usando orden RRF.")
        return [(i, 1.0) for i in indices[:top_k]]


def retrieve(query: str, filtro: dict | None = None, top_k: int = 6,
             pais: str | None = None) -> dict:
    """
    Devuelve {'chunks': [...], 'abstain': bool}.
    'filtro' = {'iso': [...], 'nist': [...]} para el espinazo estructurado.
    'pais' = código de país; incluye el núcleo universal (pais=None) + ese país.
    """
    corpus = load_data()["corpus"]
    filtro = filtro or {}

    rankings = [_bm25_rank(query)]
    dense = _dense_rank(query)
    if dense:
        rankings.append(dense)

    fused = _rrf(rankings)

    # Espinazo estructurado: boost fuerte a los chunks que casan por ID/función.
    for i in _structured(filtro):
        fused[i] = fused.get(i, 0.0) + 1.0

    ordered = sorted(fused, key=lambda i: fused[i], reverse=True)

    # Filtro por país: universal (pais=None) siempre; nacional solo si coincide.
    if pais is not None:
        ordered = [i for i in ordered if corpus[i].get("pais") in (None, pais)]
    reranked = _rerank(query, ordered[: top_k * 2], top_k)

    # Umbral de abstención (solo aplica cuando hay reranker con score real).
    client = _voyage_client()
    if client is not None:
        reranked = [(i, s) for i, s in reranked if s >= RETRIEVAL_THRESHOLD]

    chunks = []
    for i, score in reranked[:top_k]:
        chunks.append({**corpus[i], "score": round(score, 4)})

    return {"chunks": chunks, "abstain": len(chunks) == 0}
