"""Configurações: DoH, porta, upstream + personalização de tema."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from .themes import list_themes, load_theme, save_theme


class SettingsWidget(QWidget):
    """Tela de config + temas (troca em tempo real)."""

    def __init__(self, cfg, on_save, on_theme_change, parent=None) -> None:
        super().__init__(parent)
        self._cfg = cfg
        self._on_save = on_save
        self._on_theme_change = on_theme_change
        self._theme = load_theme(cfg.theme)

        layout = QVBoxLayout(self)

        g = QGroupBox("Conexão (local, sem VPS)")
        f = QFormLayout(g)
        self.port = QSpinBox()
        self.port.setRange(1024, 65535)
        self.port.setValue(cfg.proxy_port)
        f.addRow("Porta local:", self.port)
        self.doh = QComboBox()
        self.doh.addItems(["cloudflare", "google", "quad9"])
        self.doh.setCurrentText(cfg.doh_provider)
        f.addRow("DoH:", self.doh)
        self.upstream = QCheckBox("Upstream (proxies/Tor) — desligado = mais rápido")
        self.upstream.setChecked(cfg.upstream_enabled)
        f.addRow(self.upstream)
        layout.addWidget(g)

        t = QGroupBox("Aparência")
        tf = QFormLayout(t)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list_themes())
        if cfg.theme in list_themes():
            self.theme_combo.setCurrentText(cfg.theme)
        self.theme_combo.currentTextChanged.connect(self._preview_theme)
        tf.addRow("Tema:", self.theme_combo)

        row = QHBoxLayout()
        self.accent_lbl = QLabel(self._theme["accent"])
        btn_accent = QPushButton("Escolher accent…")
        btn_accent.clicked.connect(self._pick_accent)
        row.addWidget(self.accent_lbl)
        row.addWidget(btn_accent)
        tf.addRow("Cor de destaque:", row)

        self.opac = QSlider(Qt.Horizontal)
        self.opac.setRange(70, 100)
        self.opac.setValue(int(float(self._theme.get("transparency", 1.0)) * 100))
        self.opac.valueChanged.connect(self._preview_opacity)
        tf.addRow("Opacidade:", self.opac)
        layout.addWidget(t)

        btns = QHBoxLayout()
        self.btn_save = QPushButton("Salvar")
        self.btn_save.setProperty("class", "primary")
        self.btn_save.clicked.connect(self._save)
        btn_exp = QPushButton("Exportar tema…")
        btn_exp.clicked.connect(self._export)
        btn_imp = QPushButton("Importar tema…")
        btn_imp.clicked.connect(self._import)
        btns.addWidget(self.btn_save)
        btns.addWidget(btn_exp)
        btns.addWidget(btn_imp)
        layout.addLayout(btns)

        self.msg = QLabel("")
        self.msg.setProperty("class", "muted")
        layout.addWidget(self.msg)
        layout.addStretch(1)

    def _preview_theme(self, name: str) -> None:
        self._theme = load_theme(name)
        self.accent_lbl.setText(self._theme["accent"])
        self.opac.setValue(int(float(self._theme.get("transparency", 1.0)) * 100))
        self._on_theme_change(name, preview=True)

    def _pick_accent(self) -> None:
        from PySide6.QtGui import QColor

        c = QColorDialog.getColor(QColor(self._theme["accent"]), self, "Cor de destaque")
        if c.isValid():
            self._theme["accent"] = c.name()
            self.accent_lbl.setText(c.name())
            self._on_theme_change(self._theme, preview_dict=True)

    def _preview_opacity(self, v: int) -> None:
        self._theme["transparency"] = v / 100.0
        self._on_theme_change(self._theme, preview_dict=True)

    def _save(self) -> None:
        name = self.theme_combo.currentText()
        # Persiste customização de accent/opacidade no próprio json
        current = load_theme(name)
        current["accent"] = self._theme.get("accent", current["accent"])
        current["transparency"] = self._theme.get("transparency", current.get("transparency", 1.0))
        try:
            save_theme(name, current)
        except OSError as e:
            self.msg.setText(f"Falha ao salvar tema: {e}")
            return
        self._cfg.proxy_port = int(self.port.value())
        self._cfg.doh_provider = self.doh.currentText()
        self._cfg.upstream_enabled = self.upstream.isChecked()
        self._cfg.theme = name
        self._on_save()
        self.msg.setText("Salvo! Tema aplicado em tempo real.")

    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Exportar tema", f"{self.theme_combo.currentText()}.json", "*.json")
        if path:
            import json

            with open(path, "w", encoding="utf-8") as fh:
                json.dump(load_theme(self.theme_combo.currentText()), fh, indent=2, ensure_ascii=False)
            self.msg.setText(f"Tema exportado: {path}")

    def _import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Importar tema", "", "*.json")
        if path:
            import json
            from pathlib import Path

            try:
                data = json.loads(Path(path).read_text(encoding="utf-8"))
                name = Path(path).stem
                save_theme(name, data)
                self.theme_combo.clear()
                self.theme_combo.addItems(list_themes())
                self.theme_combo.setCurrentText(name)
                self.msg.setText(f"Tema '{name}' importado!")
            except (OSError, ValueError) as e:
                self.msg.setText(f"Tema inválido: {e}")
