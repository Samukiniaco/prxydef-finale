"""Laboratório: bloqueia SUA PRÓPRIA rede pra testar o Finale.

Simula o bloqueio da escola usando o arquivo hosts do Windows
(redireciona os alvos pra 127.0.0.1). Precisa rodar como ADMINISTRADOR.

Uso (PowerShell, como admin):
  py -V:3.12 tools/lab/bloquear.py bloquear      # bloqueia os alvos
  py -V:3.12 tools/lab/bloquear.py desbloquear    # libera tudo e restaura
  py -V:3.12 tools/lab/bloquear.py status         # diz se o lab está ativo

Fluxo de teste sugerido:
  1. bloquear            -> o site para de abrir (igual na escola)
  2. ligue a proteção no Finale e teste o site -> abre (DoH + proxy furam)
  3. desbloquear         -> volta ao normal

Os alvos ficam em tools/lab/alvos.txt (um por linha).
NUNCA coloque aqui os servidores de DoH (cloudflare-dns.com, dns.google...),
pois eles são a rota de fuga da própria ferramenta.
"""
from __future__ import annotations

import ctypes
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ALVOS_TXT = LAB_DIR / "alvos.txt"
BACKUP = LAB_DIR / "hosts.backup"
HOSTS = Path(r"C:\Windows\System32\drivers\etc\hosts")

INI = "# >>> PRXYDEF-LAB-INI (bloqueio de teste, remover com: bloquear.py desbloquear)"
FIM = "# <<< PRXYDEF-LAB-FIM"

# Rota de fuga da ferramenta: nunca bloquear esses.
PROTEGIDOS = {
    "cloudflare-dns.com", "dns.google", "dns.quad9.net",
    "one.one.one.one", "8.8.8.8", "1.1.1.1",
}


def is_admin() -> bool:
    """True se rodando como administrador."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def ler_alvos() -> list[str]:
    """Lê alvos.txt, pula rota de fuga com aviso."""
    alvos: list[str] = []
    for linha in ALVOS_TXT.read_text(encoding="utf-8").splitlines():
        h = linha.strip().lower().rstrip(".")
        if not h or h.startswith("#"):
            continue
        if h in PROTEGIDOS:
            print(f"  pulando {h} (é rota de fuga da ferramenta)")
            continue
        alvos.append(h)
    return alvos


def com_lab(texto: str) -> bool:
    """Diz se o hosts já tem nosso bloco."""
    return INI in texto


def tirar_bloco(texto: str) -> str:
    """Remove nosso bloco do hosts, mantendo o resto intacto."""
    linhas = texto.splitlines()
    fora: list[str] = []
    dentro = False
    for ln in linhas:
        if ln.strip() == INI:
            dentro = True
            continue
        if ln.strip() == FIM:
            dentro = False
            continue
        if not dentro:
            fora.append(ln)
    return "\n".join(fora).rstrip() + "\n"


def flush_dns() -> None:
    """Limpa cache DNS do Windows."""
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True)


def cmd_status() -> int:
    """Mostra se o laboratório está ativo."""
    texto = HOSTS.read_text(encoding="utf-8", errors="replace")
    print("LAB ATIVO (rede bloqueada)" if com_lab(texto) else "lab inativo (rede normal)")
    return 0


def cmd_bloquear() -> int:
    """Bloqueia os alvos no hosts (com backup)."""
    if not is_admin():
        print("ERRO: rode o PowerShell como ADMINISTRADOR pra bloquear.")
        return 1
    alvos = ler_alvos()
    if not alvos:
        print("ERRO: nenhum alvo válido em tools/lab/alvos.txt")
        return 1
    texto = HOSTS.read_text(encoding="utf-8", errors="replace")
    if not BACKUP.exists():
        shutil.copy2(HOSTS, BACKUP)
        print(f"backup salvo em {BACKUP}")
    texto = tirar_bloco(texto)
    bloco = [INI] + [f"127.0.0.1 {h}" for h in alvos] + [FIM]
    HOSTS.write_text(texto + "\n".join(bloco) + "\n", encoding="utf-8")
    flush_dns()
    print(f"bloqueado: {', '.join(alvos)}")
    print("teste: o site deve PARAR de abrir agora (igual na escola).")
    return 0


def cmd_desbloquear() -> int:
    """Remove o bloqueio e restaura o backup."""
    if not is_admin():
        print("ERRO: rode o PowerShell como ADMINISTRADOR pra desbloquear.")
        return 1
    texto = HOSTS.read_text(encoding="utf-8", errors="replace")
    if not com_lab(texto) and not BACKUP.exists():
        print("nada pra fazer: lab nunca foi ativado aqui.")
        return 0
    if BACKUP.exists():
        shutil.copy2(BACKUP, HOSTS)
        BACKUP.unlink()
        print("hosts restaurado do backup.")
    else:
        HOSTS.write_text(tirar_bloco(texto), encoding="utf-8")
        print("bloco removido (não havia backup).")
    flush_dns()
    print("rede de volta ao normal.")
    return 0


def main(argv: list[str]) -> int:
    """CLI do laboratório."""
    if len(argv) != 2 or argv[1] not in ("bloquear", "desbloquear", "status"):
        print(__doc__)
        return 2
    if argv[1] == "status":
        return cmd_status()
    if argv[1] == "bloquear":
        return cmd_bloquear()
    return cmd_desbloquear()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
