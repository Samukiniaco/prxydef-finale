# Changelog — Finale PrxyDef

Formato: `## [versão] - AAAA-MM-DD` + seções `Added / Changed / Fixed`.

Regra de versionamento do projeto:
- `+0.0.1` -> Patch: correções bobinhas, pouco esforço, ou adição simples de debug.
- `+0.1.0` -> Update: adições gerais, correção de bugs conhecidos, otimizações, feedbacks.
- `+1.0.0` -> Versão: revolução / mudança completa, só quando o dono pedir.
- Regra final: NUNCA publicar versionamento sem ordem explícita do dono. Até lá a versão fica estagnada.

---

## [0.0.0] - 2026-10-02
### Added
- Estrutura inicial do repo: planejamento, gitignore (com AGENTS.md local), VERSION, CHANGELOG, esqueleto src/core + ui.
- Definição do motor: DPI-bypass em modo usuário + proxy local + DoH, sem VPS obrigatório, plugin VPS futuro opcional e desligado por padrão.
