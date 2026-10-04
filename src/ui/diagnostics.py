"""Aba Diagnóstico: sites personalizáveis + DNS + bloqueio."""
from __future__ import annotations

import socket

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def check_host(host: str, port: int = 443, timeout: float = 3.0) -> tuple[bool, str]:
    """True = alcançável. Retorna (ok, detalhe)."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "OK"
    except OSError as e:
        return False, f"falhou: {e}"


class DiagnosticsWidget(QWidget):
    """Testes com lista editável de sites."""

    def __init__(self, cfg, on_save, parent=None) -> None:
        super().__init__(parent)
        self._cfg = cfg
        self._on_save = on_save

        layout = QVBoxLayout(self)

        box = QGroupBox("Sites para testar (sua lista)")
        bl = QVBoxLayout(box)
        self.list = QListWidget()
        self.list.addItems(cfg.test_hosts)
        bl.addWidget(self.list)
        row = QHBoxLayout()
        self.new_host = QLineEdit()
        self.new_host.setPlaceholderText("ex: tiktok.com")
        b_add = QPushButton("Adicionar")
        b_add.clicked.connect(self._add)
        b_del = QPushButton("Remover selecionado")
        b_del.clicked.connect(self._del)
        row.addWidget(self.new_host)
        row.addWidget(b_add)
        row.addWidget(b_del)
        bl.addLayout(row)
        prow = QHBoxLayout()
        prow.addWidget(QLabel("Porta:"))
        self.port = QSpinBox()
        self.port.setRange(1, 65535)
        self.port.setValue(443)
        prow.addWidget(self.port)
        prow.addStretch(1)
        bl.addLayout(prow)
        layout.addWidget(box)

        t = QGroupBox("Testes")
        tl = QHBoxLayout(t)
        b1 = QPushButton("Testar DNS do sistema")
        b1.clicked.connect(self._dns)
        b2 = QPushButton("Testar DoH configurado")
        b2.clicked.connect(self._doh)
        b3 = QPushButton("Checar bloqueio")
        b3.setProperty("class", "primary")
        b3.clicked.connect(self._bloq)
        b_clear = QPushButton("Limpar")
        b_clear.clicked.connect(lambda: self.log.clear())
        tl.addWidget(b1)
        tl.addWidget(b2)
        tl.addWidget(b3)
        tl.addWidget(b_clear)
        layout.addWidget(t)

        p = QGroupBox("Com a proteção LIGADA")
        pl = QHBoxLayout(p)
        b_via = QPushButton("Testar sites ATRAVÉS da proteção")
        b_via.setProperty("class", "primary")
        b_via.clicked.connect(self._via)
        b_speed = QPushButton("Medir velocidade (direto vs protegido)")
        b_speed.clicked.connect(self._speed)
        pl.addWidget(b_via)
        pl.addWidget(b_speed)
        layout.addWidget(p)

        e = QGroupBox("Raio-X (acha onde a corrente quebra)")
        el = QHBoxLayout(e)
        b_x = QPushButton("Verificar proteção de ponta a ponta")
        b_x.clicked.connect(self._xray)
        el.addWidget(b_x)
        layout.addWidget(e)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

    def hosts(self) -> list[str]:
        """Lista atual de hosts."""
        return [self.list.item(i).text() for i in range(self.list.count())]

    def _persist(self) -> None:
        self._cfg.test_hosts = self.hosts()
        self._on_save()

    def _add(self) -> None:
        h = self.new_host.text().strip().lower().rstrip(".")
        if h and h not in self.hosts():
            self.list.addItem(h)
            self.new_host.clear()
            self._persist()

    def _del(self) -> None:
        for it in self.list.selectedItems():
            self.list.takeItem(self.list.row(it))
        self._persist()

    def _dns(self) -> None:
        self.log.append("== DNS do sistema ==")
        for h in self.hosts():
            try:
                self.log.append(f"{h} -> {socket.gethostbyname(h)}")
            except OSError as e:
                self.log.append(f"{h} FALHOU: {e}")

    def _doh(self) -> None:
        from core.dns_doh import latency, resolve

        prov = self._cfg.doh_provider
        ms = latency(prov)
        self.log.append(f"== DoH ({prov}) ~ {ms:.0f}ms ==" if ms else f"== DoH ({prov}) sem resposta ==")
        for h in self.hosts():
            try:
                ips = resolve(h, prov)
                self.log.append(f"{h} -> {', '.join(ips) if ips else 'sem resposta A'}")
            except Exception as e:
                self.log.append(f"{h} DoH FALHOU: {e}")

    def _bloq(self) -> None:
        port = int(self.port.value())
        self.log.append(f"== Bloqueio :{port} ==")
        for h in self.hosts():
            host = h.split("/")[0].split(":")[0]
            ok, det = check_host(host, port)
            self.log.append(f"{h}: {'OK' if ok else 'BLOQUEADO/TIMEOUT'} ({det})")

    def _xray(self) -> None:
        """Verifica cada elo: proxy ouvindo, PAC no sistema, PAC baixável, site via proxy."""
        import httpx

        from core import proxy_local, sysproxy

        self.log.append("== Raio-X da proteção ==")
        ok = lambda c, bom, ruim: self.log.append(f"{'OK' if c else 'FALHA'}: {bom if c else ruim}")

        ouvindo = False
        try:
            with socket.create_connection(("127.0.0.1", self._cfg.proxy_port), timeout=2):
                ouvindo = True
        except OSError:
            pass
        ok(ouvindo, f"proxy ouvindo em 127.0.0.1:{self._cfg.proxy_port}",
           "proxy NÃO está ouvindo — aperte Ligar no Painel")

        esperado = f"http://127.0.0.1:{self._cfg.proxy_port}/proxy.pac"
        atual = sysproxy.current_pac()
        ok(atual == esperado, f"Windows apontando pro nosso PAC",
           f"PAC do sistema = {atual!r} (esperado {esperado!r}) — aperte Ligar de novo")

        man_on, man_srv = sysproxy.manual_proxy()
        ok(not man_on, "sem proxy manual competindo",
           f"há proxy MANUAL ativo ({man_srv}) — resto de VPN? Desligar+ligar a proteção resolve")

        baixou = False
        if ouvindo:
            try:
                r = httpx.get(esperado, timeout=5.0)
                baixou = r.status_code == 200 and "FindProxyForURL" in r.text
            except Exception:
                pass
        ok(baixou, "PAC baixável pelo navegador",
           "navegador não consegue baixar o PAC — firewall local bloqueando 127.0.0.1?")

        passou = False
        if self._cfg.enabled and proxy_local.running() and self.hosts():
            from core.speedtest import fetch_ms

            passou = fetch_ms(self.hosts()[0], self._cfg.proxy_port, timeout=8.0) is not None
        ok(passou, f"site ({self.hosts()[0] if self.hosts() else '?'}) abre ATRAVÉS da proteção",
           "site não abre nem pela proteção — veja o teste 'ATRAVÉS da proteção' p/ detalhes")
        self.log.append("Dica: Chrome aberto ANTES de Ligar guarda a config velha — feche ele todo e abra de novo.")

    def _via(self) -> None:
        """Baixa cada site passando pela proteção. Mostra DESBLOQUEADO ou não."""
        from core import proxy_local
        from core.speedtest import fetch_ms

        if not (self._cfg.enabled and proxy_local.running()):
            self.log.append("Ligue a proteção no Painel primeiro!")
            return
        self.log.append(f"== Através da proteção (127.0.0.1:{self._cfg.proxy_port}) ==")
        for h in self.hosts():
            ms = fetch_ms(h, self._cfg.proxy_port)
            if ms is None:
                self.log.append(f"{h}: AINDA BLOQUEADO (não abriu nem pela proteção)")
            else:
                self.log.append(f"{h}: DESBLOQUEADO! abriu em {ms:.0f}ms")

    def _speed(self) -> None:
        """Compara direto vs protegido pra provar que não fica lento."""
        from core import proxy_local
        from core.speedtest import compare

        port = self._cfg.proxy_port if (self._cfg.enabled and proxy_local.running()) else None
        self.log.append("== Velocidade: direto x protegido ==")
        for h in self.hosts()[:5]:
            r = compare(h, port)
            d, v = r["direto_ms"], r["protegido_ms"]
            td = f"{d:.0f}ms" if d else "falhou"
            tv = f"{v:.0f}ms" if v else ("desligada" if port is None else "falhou")
            extra = ""
            if r["perda_pct"] is not None:
                extra = f" (diferença {r['perda_pct']:+.0f}%)"
            self.log.append(f"{h}: direto {td} | protegido {tv}{extra}")
