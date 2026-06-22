"""
Cliente LLM delgado usando la API de OpenCode (OpenCode Go).

Usa el provider opencode-go (OpenAI-compatible) con la key guardada en
~/.local/share/opencode/auth.json, o OPENCODE_API_KEY si está definida.
Modelo por defecto: glm-5.2 (el mismo que alimenta opencode).

Por qué: evita depender de una key de Anthropic separada. El RAG usa la misma
cuenta de opencode que el usuario ya tiene autenticada.

Endpoint: https://opencode.ai/zen/go/v1/chat/completions
Headers: Authorization Bearer + User-Agent (Cloudflare filtra sin él).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path

OPENCODE_BASE = os.getenv("OPENCODE_BASE_URL", "https://opencode.ai/zen/go/v1")
OPENCODE_MODEL = os.getenv("OPENCODE_MODEL", "glm-5.2")
OPENCODE_UA = os.getenv("OPENCODE_USER_AGENT", "opencode/1.15.7")
AUTH_FILE = Path.home() / ".local/share/opencode/auth.json"


@lru_cache(maxsize=1)
def _api_key() -> str | None:
    """Key de opencode-go: env OPENCODE_API_KEY, o auth.json del usuario."""
    env = os.getenv("OPENCODE_API_KEY")
    if env:
        return env
    try:
        auth = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        entry = auth.get("opencode-go") or {}
        return entry.get("key")
    except Exception:
        return None


def disponible() -> bool:
    return bool(_api_key())


def chat(messages: list[dict], *, system: str | None = None,
         max_tokens: int = 2000, temperature: float = 0.2,
         model: str | None = None) -> str:
    """Llamada OpenAI-compatible. Devuelve el texto del contenido.
    Lanza RuntimeError si no hay key o la llamada falla."""
    key = _api_key()
    if not key:
        raise RuntimeError("Sin API key de OpenCode (OPENCODE_API_KEY o auth.json).")

    payload = {
        "model": model or OPENCODE_MODEL,
        "messages": ([{"role": "system", "content": system}] if system else []) + messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OPENCODE_BASE}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": OPENCODE_UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenCode API HTTP {e.code}: {e.read()[:300]!r}") from None
    content = resp["choices"][0]["message"].get("content")
    return content or ""
