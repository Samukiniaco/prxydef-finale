"""DoH + cache local (sem Qt)."""
from __future__ import annotations

import time

DOH_URLS = {
    "cloudflare": "https://cloudflare-dns.com/dns-query",
    "google": "https://dns.google/resolve",
    "quad9": "https://dns.quad9.net:5053/dns-query",
}

_cache: dict[tuple[str, str], tuple[float, list[str]]] = {}
CACHE_TTL = 120.0


def _parse_answer(payload: dict) -> list[str]:
    """Extrai IPs A/AAAA do formato dns-json (Cloudflare/Google/Quad9)."""
    out: list[str] = []
    for ans in payload.get("Answer", []) or []:
        if ans.get("type") in (1, 28) and ans.get("data"):
            out.append(str(ans["data"]))
    return out


def resolve(host: str, provider: str = "cloudflare", timeout: float = 6.0) -> list[str]:
    """Resolve host via DoH (JSON API) com cache de 2 min."""
    import httpx

    host = host.strip().lower().rstrip(".")
    key = (provider, host)
    now = time.monotonic()
    if key in _cache and now - _cache[key][0] < CACHE_TTL:
        return _cache[key][1]
    url = DOH_URLS.get(provider, DOH_URLS["cloudflare"])
    params = {"name": host, "type": "A"}
    headers = {"accept": "application/dns-json"}
    r = httpx.get(url, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    ips = _parse_answer(r.json())
    _cache[key] = (now, ips)
    return ips


def latency(provider: str = "cloudflare", timeout: float = 6.0) -> float | None:
    """Mede latência do DoH em ms (None se falhar)."""
    import httpx

    url = DOH_URLS.get(provider, DOH_URLS["cloudflare"])
    t0 = time.monotonic()
    try:
        httpx.get(url, params={"name": "example.com", "type": "A"},
                  headers={"accept": "application/dns-json"}, timeout=timeout)
        return (time.monotonic() - t0) * 1000.0
    except Exception:
        return None
