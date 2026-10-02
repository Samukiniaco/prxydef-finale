"""DPI-bypass em modo usuário (coração do projeto).

MVP: fragmentação de ClientHello TLS dentro do proxy local.
NÃO usa driver/admin. Referências de técnica: spoofDPI / zapret / GoodbyeDPI.
"""

def fragment_client_hello(data: bytes, chunk_size: int = 2) -> list[bytes]:
    """Divide ClientHello em pedaços (stub testável)."""
    return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
