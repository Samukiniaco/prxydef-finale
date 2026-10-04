"""Medidor de velocidade real: compara direto vs através da proteção."""
from __future__ import annotations

import time


def fetch_ms(url: str, proxy_port: int | None = None, timeout: float = 8.0) -> float | None:
    """Tempo em ms pra baixar a página (None se falhar).

    Se proxy_port for dado, passa pelo proxy local (a proteção).
    """
    import httpx

    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    proxies = None
    if proxy_port is not None:
        proxies = f"http://127.0.0.1:{proxy_port}"
    t0 = time.monotonic()
    try:
        with httpx.Client(proxy=proxies, timeout=timeout, follow_redirects=True) as c:
            r = c.get(url)
            r.raise_for_status()
            return (time.monotonic() - t0) * 1000.0
    except Exception:
        return None


def compare(host: str, proxy_port: int | None = None, timeout: float = 8.0) -> dict:
    """Mede direto e via proteção. Retorna dict simples."""
    direct = fetch_ms(host, None, timeout)
    via = fetch_ms(host, proxy_port, timeout) if proxy_port else None
    if direct and via:
        perda = (via - direct) / direct * 100.0
    else:
        perda = None
    return {"host": host, "direto_ms": direct, "protegido_ms": via, "perda_pct": perda}
