"""Tray icon."""
from __future__ import annotations

from PySide6.QtWidgets import QMenu, QSystemTrayIcon
from PySide6.QtGui import QAction, QIcon


def setup_tray(window) -> QSystemTrayIcon | None:
    """Cria tray com mostrar/sair. Retorna None se sem suporte."""
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None
    tray = QSystemTrayIcon(QIcon(), window)
    tray.setToolTip("Finale PrxyDef")
    menu = QMenu()
    show = QAction("Mostrar")
    show.triggered.connect(window.show)
    quit_ = QAction("Sair")
    quit_.triggered.connect(window.close)
    menu.addAction(show)
    menu.addAction(quit_)
    tray.setContextMenu(menu)
    tray.show()
    return tray
