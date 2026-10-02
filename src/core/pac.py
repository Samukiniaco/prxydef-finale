"""PAC: só domínios bloqueados passam pelo engine, resto direto."""

def generate_pac(proxy_port: int, blocked: list[str]) -> str:
    """Gera arquivo PAC (stub)."""
    domains = "\n".join(f'  "{d}",' for d in blocked)
    return f"function FindProxyForURL(url, host) {{\n  // bloqueados -> 127.0.0.1:{proxy_port}\n  // resto -> DIRECT\n  return 'DIRECT';\n}}\n// {domains}\n"
