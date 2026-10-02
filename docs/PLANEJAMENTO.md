# PLANEJAMENTO — Finale PrxyDef

## 0. Visão
Programa desktop simples, rápido e personalizável. Não é proxy web travado. Desbloqueia a nível de uso real (navegador, apps, mensagens) via técnicas locais que mantêm velocidade quase nativa.

Público: estudantes / salas / professores com proxy obrigatório que bloqueia até o básico. Filosofia: grátis, funcional, seguro, discreto (não gritar "IP suspeito").

## 1. Como funciona (sem VPS)
1. **DPI-bypass user-mode (`core/dpi_engine`)**: fragmenta ClientHello TLS, lida com SNI/ECH. Roda como proxy local, sem driver/admin.
2. **DNS criptografado (`core/dns_doh`)**: DoH/DoT + cache. Resolve bloqueios de DNS puro.
3. **Proxy local + PAC (`core/proxy_local`, `core/pac`)**: `127.0.0.1:PORTA`. Só domínios bloqueados passam pelo engine, resto direto (velocidade).
4. **Upstream pool (OFF por padrão)**: SOCKS5/HTTP públicos + adicionados pelo usuário + Tor opcional. Só se 1+2 falharem.
5. **Navegador interno (`ui/browser_tab`)**: QtWebEngine com proxy+DoH aplicados, p/ casos extremos (browser gerenciado).
6. **Futuro (stubs, não implementar agora)**: `vps_stub` (Shadowsocks/VLESS/WireGuard), `tun_stub` (WinDivert/VpnService p/ Android).

## 2. Por que rápido?
Nada de túnel pra servidor distante por padrão. 1+2 são locais, adicionam ~ms. PAC evita proxyar tudo. Upstream/VPS só se usuário ligar.

## 3. Discrição
- Default: zero chamada pra IP famoso de VPN / lista pública. DoH pra provedores comuns (Cloudflare/Google/Quad9 configurável).
- Pacote TLS fragmentado parece tráfego normal quebrado, não "cliente VPN".
- Sem conta, sem login, sem telemetria.

## 4. Personalização (requisito finale)
- `themes/*.json`: bg, fg, accent, font, radius, transparency, dark/light.
- Troca em tempo real, importar/exportar. Nada de cor hardcoded no `.py`.
- UI simples: Dashboard (status + botão ligar), Navegador, Config, Diagnóstico.

## 5. Estrutura
Ver `AGENTS.md` (local). `core/` sem Qt (testável via CLI), `ui/` só chama core.

## 6. Roadmap
- **Fase 0 (feito em 0.0.0)**: repo, planejamento, esqueleto.
- **Fase 1 MVP (alvo 0.1.0)**: config+temas, proxy local ON/OFF, DoH switch, PAC básico, diagnóstico, browser interno simples.
- **Fase 2**: dpi_engine real (fragmentação), speedtest, upstream_pool.
- **Futuro estável**: aí sim preparar Android (mesmo `core/`), depois TUN opcional.

## 7. Riscos / limites honestos
- Sem admin não dá pra fazer TUN de verdade (desbloqueio total por interface). Entregamos desbloqueio por app/proxy, que cobre 90% (sites/apps que respeitam proxy do sistema).
- DPI muito agressivo (whitelist total) só sai com VPS/TUN — por isso deixamos stubs.
- Testar sempre primeiro na própria rede.
