"""PAC real: só domínios bloqueados passam pelo engine, resto DIRECT."""
from __future__ import annotations

from pathlib import Path

PAC_PATH = Path(__file__).resolve().parents[2] / "proxy.pac"


def _js_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def generate_pac(proxy_port: int, blocked: list[str]) -> str:
    """Gera PAC funcional (FindProxyForURL)."""
    hosts = sorted({h.strip().lower().rstrip(".") for h in blocked if h.strip()})
    lines = ["function FindProxyForURL(url, host) {",
             "  host = host.toLowerCase();"]
    for h in hosts:
        lines.append(f'  if (dnsDomainIs(host, "{_js_string(h)}")) return "PROXY 127.0.0.1:{proxy_port}";')
    lines += [f'  return "DIRECT";', "}"]
    return "\n".join(lines) + "\n"


def write_pac(proxy_port: int, blocked: list[str], path: Path = PAC_PATH) -> Path:
    """Escreve proxy.pac no disco (gitignored). Retorna caminho."""
    path.write_text(generate_pac(proxy_port, blocked), encoding="utf-8")
    return path
