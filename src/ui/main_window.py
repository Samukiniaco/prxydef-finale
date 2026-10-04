"""Janela principal com abas."""
from __future__ import annotations

import logging

from PySide6.QtWidgets import QMainWindow, QTabWidget

from core.config import Config, save as save_cfg
from ui.browser_tab import BrowserTab
from ui.dashboard import DashboardWidget
from ui.diagnostics import DiagnosticsWidget
from ui.settings import SettingsWidget
from ui.themes import apply_theme, load_theme

log = logging.getLogger("prxydef.ui")


class MainWindow(QMainWindow):
    """QMainWindow com 4 abas + tema em tempo real."""

    def __init__(self, cfg: Config) -> None:
        super().__init__()
        self.cfg = cfg
        self.cfg_error: str | None = None
        self.setWindowTitle("Finale PrxyDef")
        self.resize(920, 660)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dash = DashboardWidget(
            on_toggle=self.toggle, get_status=self.dashboard_status,
            on_goto=self.tabs.setCurrentIndex,
        )
        self.browser = BrowserTab()
        self.settings = SettingsWidget(
            cfg, on_save=self.on_save, on_theme_change=self.on_theme_change
        )
        self.diag = DiagnosticsWidget(cfg, on_save=self.on_save_quiet)

        self.tabs.addTab(self.dash, "Painel")
        self.tabs.addTab(self.browser, "Navegador")
        self.tabs.addTab(self.settings, "Config")
        self.tabs.addTab(self.diag, "Diagnóstico")

        from core import sysproxy as _sp

        if _sp.cleanup_stale():
            self.cfg.enabled = False
        self.apply_current_theme()

    # --- engine real: proxy local + PAC no sistema ---
    def toggle(self) -> None:
        """Liga/desliga proteção (proxy local + PAC no sistema, restaura ao sair)."""
        from core import proxy_local
        from core import pac as pac_mod
        from core import sysproxy

        if self.cfg.enabled:
            sysproxy.restore()
            proxy_local.set_pac(None)
            proxy_local.stop()
            self.cfg.enabled = False
            self.cfg_error = None
        else:
            self.cfg_error = None
            if not proxy_local.start(self.cfg.proxy_port):
                self.cfg_error = proxy_local.last_error() or "proxy não subiu"
                log.error("proxy não subiu: %s", self.cfg_error)
                return
            self.cfg.enabled = True
            if self.cfg.apply_sysproxy:
                texto = pac_mod.generate_pac(self.cfg.proxy_port, self.cfg.test_hosts)
                proxy_local.set_pac(texto)
                pac_mod.write_pac(self.cfg.proxy_port, self.cfg.test_hosts)  # backup
                sysproxy.apply_pac(f"http://127.0.0.1:{self.cfg.proxy_port}/proxy.pac")

    def dashboard_status(self) -> dict:
        """Dict completo pro painel principal."""
        from core import proxy_local
        from core import sysproxy

        on = bool(self.cfg.enabled and proxy_local.running())
        sys_on = bool(sysproxy.current_pac())
        if self.cfg_error and not on:
            detail = f"NÃO LIGOU: {self.cfg_error}. Feche outra cópia do app e tente de novo."
        else:
            detail = (
                f"127.0.0.1:{self.cfg.proxy_port} • DoH {self.cfg.doh_provider}"
                + (" • PAC no sistema" if sys_on else "")
                if on else
                f"Pronto — porta {self.cfg.proxy_port}, tema {self.cfg.theme}. Aperte Ligar."
            )
        return {
            "enabled": on,
            "detail": detail,
            "proxy": f"127.0.0.1:{self.cfg.proxy_port}\n{'ATIVO' if on else 'parado'}",
            "dns": f"DoH: {self.cfg.doh_provider}\nCache local 2min",
            "mode": "PAC: só bloqueado\npassa pelo engine" + (" (sistema)" if sys_on else ""),
            "upstream": "ON (fallback)" if self.cfg.upstream_enabled else "OFF (mais rápido)",
        }

    # --- temas / config ---
    def apply_current_theme(self) -> None:
        """Aplica tema atual em tempo real."""
        apply_theme(self, load_theme(self.cfg.theme))

    def on_save(self) -> None:
        """Salva config.local.json e reaplica."""
        save_cfg(self.cfg)
        self.apply_current_theme()
        self.dash.refresh()

    def on_save_quiet(self) -> None:
        """Salva sem reaplicar tema (usado pela lista de sites)."""
        save_cfg(self.cfg)
        self.dash.refresh()

    def on_theme_change(self, name_or_dict, preview: bool = False, preview_dict: bool = False) -> None:
        """Preview em tempo real sem salvar."""
        if preview_dict:
            apply_theme(self, name_or_dict)  # type: ignore[arg-type]
        elif preview:
            self.cfg.theme = str(name_or_dict)
            self.apply_current_theme()

    def closeEvent(self, event) -> None:  # noqa: N802
        """Garante proxy parado + sistema restaurado ao fechar."""
        try:
            from core import proxy_local, sysproxy

            sysproxy.restore()
            proxy_local.stop()
        finally:
            super().closeEvent(event)
