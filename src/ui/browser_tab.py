"""Navegador interno QtWebEngine (casos extremos)."""
from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


class BrowserTab(QWidget):
    """Barra estilo navegador: voltar/avançar no canto superior esquerdo."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.back = QPushButton("◀")
        self.back.setFixedWidth(44)
        self.back.setToolTip("Voltar")
        self.fwd = QPushButton("▶")
        self.fwd.setFixedWidth(44)
        self.fwd.setToolTip("Avançar")
        self.reload = QPushButton("⟳")
        self.reload.setFixedWidth(44)
        self.reload.setToolTip("Recarregar")
        self.home = QPushButton("⌂")
        self.home.setFixedWidth(44)
        self.home.setToolTip("Início")
        self.url = QLineEdit("https://example.com")
        go = QPushButton("Ir")
        go.setProperty("class", "primary")
        go.clicked.connect(self._go)
        self.url.returnPressed.connect(self._go)
        for b in (self.back, self.fwd, self.reload, self.home):
            bar.addWidget(b)
        bar.addWidget(self.url, 1)
        bar.addWidget(go)
        layout.addLayout(bar)
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView

            self.view = QWebEngineView()
            self.view.setUrl(QUrl("https://example.com"))
            self.view.urlChanged.connect(lambda q: self.url.setText(q.toString()))
            self.view.loadFinished.connect(self._sync_nav)
            self.back.clicked.connect(self.view.back)
            self.fwd.clicked.connect(self.view.forward)
            self.reload.clicked.connect(self.view.reload)
            self.home.clicked.connect(lambda: self.view.setUrl(QUrl("https://example.com")))
            layout.addWidget(self.view)
            self._sync_nav()
        except ImportError:
            self.view = None  # type: ignore[assignment]
            layout.addWidget(QLabel("QtWebEngine não disponível neste build."))
            for b in (self.back, self.fwd, self.reload, self.home):
                b.setEnabled(False)

    def _go(self) -> None:
        if self.view is None:
            return
        u = self.url.text().strip()
        if not u.startswith(("http://", "https://")):
            u = "https://" + u
        self.view.setUrl(QUrl(u))

    def _sync_nav(self, *_args) -> None:
        if self.view is None:
            return
        try:
            hist = self.view.history()
            self.back.setEnabled(hist.canGoBack())
            self.fwd.setEnabled(hist.canGoForward())
        except Exception:
            pass
