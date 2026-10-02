"""Config do usuário (sem Qt)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.local.json"

DEFAULT_HOSTS = ["google.com", "youtube.com", "discord.com"]


@dataclass
class Config:
    """Config mínima da UI."""

    proxy_port: int = 8899
    doh_provider: str = "cloudflare"  # cloudflare | google | quad9
    theme: str = "dark"
    upstream_enabled: bool = False
    test_hosts: list[str] = field(default_factory=lambda: list(DEFAULT_HOSTS))
    apply_sysproxy: bool = True  # aplicar PAC no proxy do sistema ao ligar
    # Estado apenas em memória (não salva): engine ligado/desligado
    enabled: bool = False


def load(path: Path = CONFIG_PATH) -> Config:
    """Carrega config.local.json se existir, senão defaults."""
    cfg = Config()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for k in ("proxy_port", "doh_provider", "theme", "upstream_enabled", "apply_sysproxy"):
                if k in data:
                    setattr(cfg, k, data[k])
            if isinstance(data.get("test_hosts"), list):
                hosts = [str(h).strip() for h in data["test_hosts"] if str(h).strip()]
                if hosts:
                    cfg.test_hosts = hosts[:20]  # limite p/ não virar bagunça
        except (OSError, ValueError):
            return Config()
    return cfg


def save(cfg: Config, path: Path = CONFIG_PATH) -> None:
    """Salva config (sem o campo enabled, que é sessão)."""
    data = asdict(cfg)
    data.pop("enabled", None)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
