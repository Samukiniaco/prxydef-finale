"""Config do usuário (sem Qt)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.local.json"


@dataclass
class Config:
    """Config mínima da UI."""

    proxy_port: int = 8899
    doh_provider: str = "cloudflare"  # cloudflare | google | quad9
    theme: str = "dark"
    upstream_enabled: bool = False
    # Estado apenas em memória (não salva): engine ligado/desligado
    enabled: bool = False


def load(path: Path = CONFIG_PATH) -> Config:
    """Carrega config.local.json se existir, senão defaults."""
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cfg = Config()
            for k in ("proxy_port", "doh_provider", "theme", "upstream_enabled"):
                if k in data:
                    setattr(cfg, k, data[k])
            return cfg
        except (OSError, ValueError):
            return Config()
    return Config()


def save(cfg: Config, path: Path = CONFIG_PATH) -> None:
    """Salva config (sem o campo enabled, que é sessão)."""
    data = asdict(cfg)
    data.pop("enabled", None)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
