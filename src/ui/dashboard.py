"""Dashboard: painel principal (status + atalhos)."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class DashboardWidget(QWidget):
    """Painel principal completo e intuitivo."""

    def __init__(self, on_toggle, get_status, on_goto, parent=None) -> None:
        super().__init__(parent)
        self._on_toggle = on_toggle
        self._get_status = get_status
        self._on_goto = on_goto

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Finale PrxyDef")
        title.setProperty("class", "title")
        layout.addWidget(title)
        sub = QLabel("Rede bloqueada agindo como desbloqueada — rápido, local, sem VPN.")
        sub.setProperty("class", "muted")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        # --- cartão hero: status + botão grande ---
        hero = QGroupBox("Status da proteção")
        hl = QHBoxLayout(hero)
        left = QVBoxLayout()
        self.dot = QLabel("○")
        self.dot.setStyleSheet("font-size: 40px;")
        left.addWidget(self.dot)
        hl.addLayout(left)
        mid = QVBoxLayout()
        self.status = QLabel("Desligado")
        self.status.setStyleSheet("font-size: 17px; font-weight: bold;")
        mid.addWidget(self.status)
        self.info = QLabel("")
        self.info.setProperty("class", "muted")
        self.info.setWordWrap(True)
        mid.addWidget(self.info)
        hl.addLayout(mid, 1)
        self.btn = QPushButton("Ligar proteção")
        self.btn.setProperty("class", "primary")
        self.btn.setMinimumHeight(52)
        self.btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn.clicked.connect(self._toggle)
        hl.addWidget(self.btn)
        layout.addWidget(hero)

        # --- grade de cartões: proxy / dns / modo / upstream ---
        grid = QGridLayout()
        grid.setSpacing(12)
        self.card_proxy = self._card("Proxy local", "...")
        self.card_dns = self._card("DNS (DoH)", "...")
        self.card_mode = self._card("Modo", "...")
        self.card_up = self._card("Upstream", "...")
        grid.addWidget(self.card_proxy[0], 0, 0)
        grid.addWidget(self.card_dns[0], 0, 1)
        grid.addWidget(self.card_mode[0], 1, 0)
        grid.addWidget(self.card_up[0], 1, 1)
        layout.addLayout(grid)

        # --- atalhos ---
        box = QGroupBox("Atalhos")
        row = QHBoxLayout(box)
        b_test = QPushButton("Testar bloqueios")
        b_test.clicked.connect(lambda: self._on_goto(3))
        b_nav = QPushButton("Abrir navegador")
        b_nav.clicked.connect(lambda: self._on_goto(1))
        b_cfg = QPushButton("Ajustes / temas")
        b_cfg.clicked.connect(lambda: self._on_goto(2))
        row.addWidget(b_test)
        row.addWidget(b_nav)
        row.addWidget(b_cfg)
        layout.addWidget(box)

        tip = QLabel("Dica: ligue, depois teste seus sites na aba Diagnóstico. Só o bloqueado passa pelo engine — o resto vai direto (velocidade).")
        tip.setProperty("class", "muted")
        tip.setWordWrap(True)
        layout.addWidget(tip)
        layout.addStretch(1)
        self.refresh()

    def _card(self, title: str, value: str) -> tuple[QFrame, QLabel]:
        box = QGroupBox(title)
        vl = QVBoxLayout(box)
        lbl = QLabel(value)
        lbl.setWordWrap(True)
        vl.addWidget(lbl)
        return box, lbl

    def _toggle(self) -> None:
        self._on_toggle()
        self.refresh()

    def refresh(self) -> None:
        """Atualiza todos os cartões com dict do MainWindow."""
        s = self._get_status()
        on = bool(s.get("enabled"))
        self.dot.setText("●" if on else "○")
        self.status.setText("Proteção LIGADA — proxy local ativo" if on else "Proteção desligada")
        self.info.setText(str(s.get("detail", "")))
        self.btn.setText("Desligar" if on else "Ligar proteção")
        self.card_proxy[1].setText(str(s.get("proxy", "")))
        self.card_dns[1].setText(str(s.get("dns", "")))
        self.card_mode[1].setText(str(s.get("mode", "")))
        self.card_up[1].setText(str(s.get("upstream", "")))
