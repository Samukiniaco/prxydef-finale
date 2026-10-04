"""Proxy do sistema (Windows via HKCU, sem admin). Restaura tudo ao desligar."""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass

log = logging.getLogger("prxydef.sysproxy")


@dataclass
class PreviousState:
    """Backup do que existia antes de ligarmos."""

    auto_config_url: str | None = None
    proxy_enable: int = 0
    proxy_server: str | None = None
    proxy_override: str | None = None


_saved: PreviousState | None = None


def _win_key(create: bool = False):
    import winreg

    return winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        0,
        winreg.KEY_READ | (winreg.KEY_WRITE if create else 0),
    )


def _read(key, name: str):
    try:
        import winreg

        val, _ = winreg.QueryValueEx(key, name)
        return val
    except OSError:
        return None


def _notify_windows() -> None:
    """Avisa o Windows que as configs de proxy mudaram (sem reboot)."""
    import ctypes

    INTERNET_OPTION_SETTINGS_CHANGED = 39
    INTERNET_OPTION_REFRESH = 37
    try:
        internet = ctypes.windll.wininet
        internet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        internet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
    except Exception as e:
        log.warning("falha ao notificar Windows: %s", e)


def apply_pac(pac_file_url: str) -> bool:
    """Aponta o proxy do sistema pro nosso PAC. Retorna True se aplicou."""
    global _saved
    if sys.platform != "win32":
        log.info("proxy do sistema automático só no Windows por enquanto")
        return False
    import winreg

    key = _win_key()
    prev = PreviousState(
        auto_config_url=_read(key, "AutoConfigURL"),
        proxy_enable=int(_read(key, "ProxyEnable") or 0),
        proxy_server=_read(key, "ProxyServer"),
        proxy_override=_read(key, "ProxyOverride"),
    )
    key.Close()
    _saved = prev
    key = _win_key(create=True)
    try:
        winreg.SetValueEx(key, "AutoConfigURL", 0, winreg.REG_SZ, pac_file_url)
        # Proxy manual LIGADO junto com PAC confunde o navegador (ex: resto de
        # VPN que falhou). Desligamos o manual; o backup acima restaura depois.
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
    finally:
        key.Close()
    _notify_windows()
    log.info("proxy do sistema -> PAC %s", pac_file_url)
    return True


def restore() -> bool:
    """Restaura o que existia antes. Retorna True se mexeu em algo."""
    global _saved
    if sys.platform != "win32":
        return False
    import winreg

    key = _win_key(create=True)
    try:
        if _saved is not None and _saved.auto_config_url:
            winreg.SetValueEx(key, "AutoConfigURL", 0, winreg.REG_SZ, _saved.auto_config_url)
        else:
            try:
                winreg.DeleteValue(key, "AutoConfigURL")
            except OSError:
                pass
        # Restaura o proxy manual exatamente como estava (ou desliga se não havia).
        if _saved is not None:
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, int(_saved.proxy_enable or 0))
            if _saved.proxy_server:
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, _saved.proxy_server)
            else:
                try:
                    winreg.DeleteValue(key, "ProxyServer")
                except OSError:
                    pass
            if _saved.proxy_override:
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, _saved.proxy_override)
    finally:
        key.Close()
        _saved = None
    _notify_windows()
    log.info("proxy do sistema restaurado")
    return True


def current_pac() -> str | None:
    """URL do PAC atual do sistema (None se não há)."""
    if sys.platform != "win32":
        return None
    key = _win_key()
    try:
        return _read(key, "AutoConfigURL")
    finally:
        key.Close()


def manual_proxy() -> tuple[int, str | None]:
    """Retorna (ProxyEnable, ProxyServer) atual. Para o auto-diagnóstico."""
    if sys.platform != "win32":
        return 0, None
    key = _win_key()
    try:
        return int(_read(key, "ProxyEnable") or 0), _read(key, "ProxyServer")
    finally:
        key.Close()


def cleanup_stale() -> bool:
    """Remove PAC apontando pro nosso proxy.pac se ele não está rodando.

    Cura restos de versões antigas (ex: PAC em file:// que o navegador ignora).
    Só mexe se a URL contiver 'proxy.pac'. Retorna True se limpou.
    """
    if sys.platform != "win32":
        return False
    import winreg

    atual = current_pac()
    if not atual or "proxy.pac" not in atual:
        return False
    key = _win_key(create=True)
    try:
        try:
            winreg.DeleteValue(key, "AutoConfigURL")
        except OSError:
            return False
    finally:
        key.Close()
    _notify_windows()
    log.info("PAC obsoleto removido: %s", atual)
    return True
