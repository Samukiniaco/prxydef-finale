# Changelog — Finale PrxyDef

Formato: `## [versão] - AAAA-MM-DD` + seções `Added / Changed / Fixed`.

Regra de versionamento do projeto:
- `+0.0.1` -> Patch: correções bobinhas, pouco esforço, ou adição simples de debug.
- `+0.1.0` -> Update: adições gerais, correção de bugs conhecidos, otimizações, feedbacks.
- `+1.0.0` -> Versão: revolução / mudança completa, só quando o dono pedir.
- Regra final: NUNCA publicar versionamento sem ordem explícita do dono. Até lá a versão fica estagnada.

---

## [0.1.0] - 2026-10-02
### Added
- UI completa em PySide6: Painel (status + ligar/desligar + atalhos), Navegador interno (voltar/avançar), Config (DoH, porta, upstream + temas em tempo real claro/escuro, import/export), Diagnóstico (sites personalizáveis, DNS sistema/DoH, checagem de bloqueio).
- Proxy local HTTP/CONNECT real em 127.0.0.1:porta (thread daemon + asyncio) com fragmentação de ClientHello (DPI-bypass user-mode).
- DoH real (Cloudflare/Google/Quad9) com cache local + medição de latência.
- Temas `dark.json`/`light.json` expandidos (card, muted, transparency).

## [0.0.0] - 2026-10-02
### Added
- Estrutura inicial do repo: planejamento, gitignore (com AGENTS.md local), VERSION, CHANGELOG, esqueleto src/core + ui.
- Definição do motor: DPI-bypass em modo usuário + proxy local + DoH, sem VPS obrigatório, plugin VPS futuro opcional e desligado por padrão.
