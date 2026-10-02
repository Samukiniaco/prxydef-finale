"""Carrega themes/*.json, aplica em tempo real, sem cor hardcoded."""
import json
from pathlib import Path

def load_theme(name: str = "dark") -> dict:
    """Carrega tema (stub testável)."""
    p = Path(__file__).resolve().parents[2] / "themes" / f"{name}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}
