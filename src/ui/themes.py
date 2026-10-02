"""Carrega themes/*.json, aplica em tempo real, sem cor hardcoded."""
from __future__ import annotations

import json
from pathlib import Path

THEMES_DIR = Path(__file__).resolve().parents[2] / "themes"

DEFAULTS = {
    "name": "dark",
    "bg": "#1b1e24",
    "card": "#242832",
    "fg": "#e8eaf0",
    "muted": "#9aa3b2",
    "accent": "#4da3ff",
    "font": "Segoe UI",
    "radius": 10,
    "transparency": 0.95,
}


def list_themes() -> list[str]:
    """Lista nomes de temas disponíveis em themes/*.json."""
    if not THEMES_DIR.exists():
        return ["dark"]
    return sorted(p.stem for p in THEMES_DIR.glob("*.json"))


def load_theme(name: str = "dark") -> dict:
    """Carrega tema mesclado com defaults (nunca quebra se faltar chave)."""
    data = dict(DEFAULTS)
    p = THEMES_DIR / f"{name}.json"
    if p.exists():
        try:
            data.update(json.loads(p.read_text(encoding="utf-8")))
        except ValueError:
            pass
    data["name"] = name if not data.get("name") else data["name"]
    return data


def save_theme(name: str, theme: dict) -> None:
    """Salva tema customizado em themes/<name>.json."""
    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    p = THEMES_DIR / f"{name}.json"
    p.write_text(json.dumps(theme, indent=2, ensure_ascii=False), encoding="utf-8")


def build_qss(t: dict) -> str:
    """Monta QSS só com valores do tema (nada hardcoded)."""
    bg = t["bg"]
    card = t.get("card", bg)
    fg = t["fg"]
    muted = t.get("muted", fg)
    accent = t["accent"]
    font = t.get("font", "Segoe UI")
    radius = int(t.get("radius", 10))
    return f"""
* {{ font-family: "{font}"; }}
QMainWindow, QWidget {{ background: {bg}; color: {fg}; }}
QTabWidget::pane {{ border: 1px solid {card}; border-radius: {radius}px; }}
QTabBar::tab {{ background: {card}; color: {muted}; padding: 8px 16px; border-top-left-radius: {radius}px; border-top-right-radius: {radius}px; }}
QTabBar::tab:selected {{ background: {accent}; color: white; }}
QGroupBox {{ border: 1px solid {card}; border-radius: {radius}px; margin-top: 12px; padding: 12px; }}
QGroupBox::title {{ color: {muted}; }}
QPushButton {{ background: {card}; color: {fg}; border: 1px solid {card}; border-radius: {radius}px; padding: 8px 16px; }}
QPushButton:hover {{ border: 1px solid {accent}; }}
QPushButton[class="primary"] {{ background: {accent}; color: white; border: none; font-weight: bold; }}
QLineEdit, QSpinBox, QComboBox {{ background: {card}; color: {fg}; border: 1px solid {card}; border-radius: {radius//2}px; padding: 6px; }}
QTextEdit {{ background: {card}; color: {fg}; border: 1px solid {card}; border-radius: {radius//2}px; }}
QLabel[class="muted"] {{ color: {muted}; }}
QLabel[class="title"] {{ font-size: 18px; font-weight: bold; }}
QCheckBox {{ color: {fg}; }}
QSlider::handle {{ background: {accent}; }}
"""


def apply_theme(app_or_widget, theme: dict) -> None:
    """Aplica QSS + opacidade (tempo real)."""
    qss = build_qss(theme)
    try:
        app_or_widget.setStyleSheet(qss)
    except AttributeError:
        pass
    try:
        # Transparência da janela principal (1.0 = opaco)
        from PySide6.QtWidgets import QMainWindow

        if isinstance(app_or_widget, QMainWindow):
            app_or_widget.setWindowOpacity(float(theme.get("transparency", 1.0)))
    except Exception:
        pass
