"""Aba Diagnóstico: DNS + bloqueio (usa só stdlib, sem Qt no core)."""
from __future__ import annotations

import socket

from PySide6.QtWidgets import QGroupBox, QPushButton, QTextEdit, QVBoxLayout, QWidget


def check_host(host: str, port: int = 443, timeout: float = 3.0) -> tuple[bool, str]:
    """True = alcançável. Retorna (ok, detalhe)."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "OK"
    except OSError as e:
        return False, f"falhou: {e}"


class DiagnosticsWidget(QWidget):
    """Botões simples de debug de rede."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        box = QGroupBox("Testes rápidos")
        bl = QVBoxLayout(box)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        b1 = QPushButton("Testar DNS do sistema")
        b1.clicked.connect(self._dns)
        b2 = QPushButton("Checar bloqueio (443)")
        b2.clicked.connect(self._bloq)
        bl.addWidget(b1)
        bl.addWidget(b2)
        layout.addWidget(box)
        layout.addWidget(self.log)

    def _dns(self) -> None:
        self.log.append("== DNS do sistema ==")
        for h in ["google.com", "youtube.com", "discord.com"]:
            try:
                self.log.append(f"{h} -> {socket.gethostbyname(h)}")
            except OSError as e:
                self.log.append(f"{h} FALHOU: {e}")

    def _bloq(self) -> None:
        self.log.append("== Bloqueio :443 ==")
        for h in ["google.com", "youtube.com", "discord.com", "1.1.1.1"]:
            ok, det = check_host(h)
            self.log.append(f"{h}: {'OK' if ok else 'BLOQUEADO/TIMEOUT'} ({det})")
