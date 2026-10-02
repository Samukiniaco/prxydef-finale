"""Dashboard: status + botão ligar/desligar."""
from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout, QWidget


class DashboardWidget(QWidget):
    """Tela principal simples."""

    def __init__(self, on_toggle, get_status_text, parent=None) -> None:
        super().__init__(parent)
        self._on_toggle = on_toggle
        self._get_status_text = get_status_text

        layout = QVBoxLayout(self)
        title = QLabel("Finale PrxyDef")
        title.setProperty("class", "title")
        layout.addWidget(title)

        sub = QLabel("Rede bloqueada agindo como desbloqueada — rápido e local.")
        sub.setProperty("class", "muted")
        layout.addWidget(sub)

        box = QGroupBox("Status")
        bl = QVBoxLayout(box)
        self.status = QLabel("Desligado")
        bl.addWidget(self.status)
        self.info = QLabel("")
        self.info.setProperty("class", "muted")
        bl.addWidget(self.info)
        self.btn = QPushButton("Ligar")
        self.btn.setProperty("class", "primary")
        self.btn.clicked.connect(self._toggle)
        bl.addWidget(self.btn)
        layout.addWidget(box)
        layout.addStretch(1)
        self.refresh()

    def _toggle(self) -> None:
        self._on_toggle()
        self.refresh()

    def refresh(self) -> None:
        """Atualiza textos (chamado após toggle ou troca de config)."""
        ligado, detalhe = self._get_status_text()
        self.status.setText("● Ligado (proxy local ativo)" if ligado else "○ Desligado")
        self.info.setText(detalhe)
        self.btn.setText("Desligar" if ligado else "Ligar")
