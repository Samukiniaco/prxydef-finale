# Finale PrxyDef

Desbloqueador de rede rápido (programa desktop, não site). Objetivo: rede bloqueada "age como desbloqueada" — sites + apps + mensagens — sem VPN lenta obrigatória.

Núcleo 100% local: DPI-bypass em modo usuário + proxy local + DoH. Sem VPS obrigatório. Plugin VPS futuro opcional e desligado por padrão.

> Status: `0.0.0` — estrutura inicial. Veja `CHANGELOG.md`. Versionamento só publica com ordem do dono.

## Rodar (dev)
```bash
pip install -r requirements.txt
python src/main.py
```

## Build
```bash
pyinstaller --onefile --windowed src/main.py
```

## Docs
- `docs/PLANEJAMENTO.md` — como funciona, motor, personalização, roadmap.
- `tools/debug_dns.py` e `tools/check_bloqueio.py` — diagnóstico de rede.
