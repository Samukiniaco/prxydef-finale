"""DoH/DoT + cache local (stub)."""
DOH_URLS = {
    "cloudflare": "https://cloudflare-dns.com/dns-query",
    "google": "https://dns.google/resolve",
    "quad9": "https://dns.quad9.net:5053/dns-query",
}

def resolve(host: str, provider: str = "cloudflare") -> list[str]:
    """Resolve host via DoH (implementar no MVP com httpx + cache)."""
    raise NotImplementedError("MVP: implementar DoH + cache")
