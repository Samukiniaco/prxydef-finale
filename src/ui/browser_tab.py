"""Navegador interno QtWebEngine com proxy+DoH (casos extremos)."""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


class BrowserTab(QWidget):
    """Aba de navegador interno (degrada graciosamente sem WebEngine)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.url = QLineEdit("https://example.com")
        go = QPushButton("Ir")
        go.clicked.connect(self._go)
        bar.addWidget(self.url)
        bar.addWidget(go)
        layout.addLayout(bar)
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView

            self.view = QWebEngineView()
            self.view.setUrl("https://example.com")
            layout.addWidget(self.view)
        except ImportError:
            layout.addWidget(QLabel("QtWebEngine não disponível neste build."))

    def _go(self) -> None:
        u = self.url.text().strip()
        if not u.startswith(("http://", "https://")):
            u = "https://" + u
        try:
            self.view.setUrl(u)
        except AttributeError:
            pass
