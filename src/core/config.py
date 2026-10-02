"""Config do usuário (sem Qt)."""
from dataclasses import dataclass, field

@dataclass
class Config:
    """Config mínima do MVP."""
    proxy_port: int = 8899
    doh_provider: str = "cloudflare"  # cloudflare | google | quad9
    theme: str = "dark"
    upstream_enabled: bool = False

def load() -> Config:
    """Carrega config (stub — lê config.local.json no MVP)."""
    return Config()

def save(cfg: Config) -> None:
    """Salva config (stub)."""
    pass
