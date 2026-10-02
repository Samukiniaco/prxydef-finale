"""Ponto de entrada do Finale PrxyDef."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.INFO)

try:
    from PySide6.QtWidgets import QApplication
    from core.config import load as load_cfg
    from ui.main_window import MainWindow
    from ui.tray import setup_tray
except ImportError as e:
    print(f"Falta dependência: {e}\nRode: py -V:3.12 -m pip install -r requirements.txt")
    raise SystemExit(1)


def main() -> int:
    """Sobe QApplication + MainWindow."""
    app = QApplication(sys.argv)
    cfg = load_cfg()
    win = MainWindow(cfg)
    win.show()
    setup_tray(win)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
