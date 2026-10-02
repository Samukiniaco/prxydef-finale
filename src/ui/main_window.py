"""Janela principal com abas."""
from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from core.config import Config, save as save_cfg
from ui.browser_tab import BrowserTab
from ui.dashboard import DashboardWidget
from ui.diagnostics import DiagnosticsWidget
from ui.settings import SettingsWidget
from ui.themes import apply_theme, load_theme


class MainWindow(QMainWindow):
    """QMainWindow com 4 abas + tema em tempo real."""

    def __init__(self, cfg: Config) -> None:
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle("Finale PrxyDef")
        self.resize(880, 620)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dash = DashboardWidget(
            on_toggle=self.toggle, get_status_text=self.status_text
        )
        self.browser = BrowserTab()
        self.settings = SettingsWidget(
            cfg, on_save=self.on_save, on_theme_change=self.on_theme_change
        )
        self.diag = DiagnosticsWidget()

        self.tabs.addTab(self.dash, "Painel")
        self.tabs.addTab(self.browser, "Navegador")
        self.tabs.addTab(self.settings, "Config")
        self.tabs.addTab(self.diag, "Diagnóstico")

        self.apply_current_theme()

    # --- engine (stub por enquanto: só estado em memória) ---
    def toggle(self) -> None:
        """Liga/desliga proxy local (engine real entra na Fase 2)."""
        self.cfg.enabled = not self.cfg.enabled

    def status_text(self) -> tuple[bool, str]:
        """(ligado, detalhe) pro dashboard."""
        if self.cfg.enabled:
            det = f"127.0.0.1:{self.cfg.proxy_port} • DoH {self.cfg.doh_provider}"
            if self.cfg.upstream_enabled:
                det += " • upstream ON"
            return True, det
        return False, f"Pronto — porta {self.cfg.proxy_port}, tema {self.cfg.theme}"

    # --- temas / config ---
    def apply_current_theme(self) -> None:
        """Aplica tema atual em tempo real."""
        apply_theme(self, load_theme(self.cfg.theme))

    def on_save(self) -> None:
        """Salva config.local.json e reaplica."""
        save_cfg(self.cfg)
        self.apply_current_theme()
        self.dash.refresh()

    def on_theme_change(self, name_or_dict, preview: bool = False, preview_dict: bool = False) -> None:
        """Preview em tempo real sem salvar."""
        if preview_dict:
            apply_theme(self, name_or_dict)  # type: ignore[arg-type]
        elif preview:
            self.cfg.theme = str(name_or_dict)
            self.apply_current_theme()
