"""Proxy HTTP/CONNECT local 127.0.0.1:porta (asyncio em thread daemon).

Suporta o que apps/navegadores precisam: GET http://... e CONNECT host:porta.
Hook de DPI: primeiro pacote do cliente que pareça TLS ClientHello (0x16 0x03)
é enviado fragmentado, p/ quebrar inspeção simples sem perder velocidade.
"""
from __future__ import annotations

import asyncio
import logging
import threading

log = logging.getLogger("prxydef.proxy")

_loop: asyncio.AbstractEventLoop | None = None
_thread: threading.Thread | None = None
_server: asyncio.AbstractServer | None = None
_running_port: int | None = None
_lock = threading.Lock()


def is_tls_client_hello(data: bytes) -> bool:
    """Heurística mínima: record TLS handshake (0x16 0x03 ...)."""
    return len(data) > 5 and data[0] == 0x16 and data[1] == 0x03


async def _pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while True:
            chunk = await reader.read(65536)
            if not chunk:
                break
            writer.write(chunk)
            await writer.drain()
    except (ConnectionError, asyncio.IncompleteReadError):
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def _send_fragmented(writer: asyncio.StreamWriter, data: bytes) -> None:
    """Envia ClientHello em 2 pedaços (DPI-bypass user-mode simples)."""
    cut = max(1, min(len(data) - 1, 3))
    writer.write(data[:cut])
    await writer.drain()
    await asyncio.sleep(0)
    writer.write(data[cut:])
    await writer.drain()


def _parse_target(request_line: str, headers: dict[str, str]) -> tuple[str, int] | None:
    parts = request_line.split()
    if len(parts) < 2:
        return None
    method, target = parts[0].upper(), parts[1]
    if method == "CONNECT":
        host, _, port = target.partition(":")
        return host, int(port or 443)
    # GET http://host:porta/path
    if "://" in target:
        rest = target.split("://", 1)[1]
        hostport = rest.split("/", 1)[0]
        host, _, port = hostport.partition(":")
        default = 443 if target.startswith("https") else 80
        return host, int(port or default)
    # GET /path com Host:
    hostport = headers.get("host", "")
    host, _, port = hostport.partition(":")
    if host:
        return host, int(port or 80)
    return None


async def _handle(client_r: asyncio.StreamReader, client_w: asyncio.StreamWriter) -> None:
    remote_w: asyncio.StreamWriter | None = None
    try:
        head = await client_r.readuntil(b"\r\n\r\n")
    except (asyncio.LimitOverrunError, asyncio.IncompleteReadError, ConnectionError):
        client_w.close()
        return
    try:
        text = head.decode("latin-1")
    except UnicodeDecodeError:
        client_w.close()
        return
    lines = text.split("\r\n")
    headers: dict[str, str] = {}
    for ln in lines[1:]:
        if ":" in ln:
            k, _, v = ln.partition(":")
            headers[k.strip().lower()] = v.strip()
    target = _parse_target(lines[0] if lines else "", headers)
    if not target:
        client_w.write(b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n")
        await client_w.drain()
        client_w.close()
        return
    host, port = target
    try:
        remote_r, remote_w = await asyncio.open_connection(host, port)
    except OSError:
        try:
            client_w.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
            await client_w.drain()
        finally:
            client_w.close()
        return
    method = lines[0].split()[0].upper() if lines and lines[0] else ""
    try:
        if method == "CONNECT":
            client_w.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await client_w.drain()
        else:
            # Reencaminha request-line com path relativo + headers
            target_path = "/"
            req_target = lines[0].split()[1] if len(lines[0].split()) > 1 else "/"
            if "://" in req_target:
                target_path = "/" + req_target.split("://", 1)[1].split("/", 1)[1] if "/" in req_target.split("://", 1)[1] else "/"
            else:
                target_path = req_target
            fwd = f"{method} {target_path} HTTP/1.1\r\n"
            for ln in lines[1:]:
                if not ln:
                    continue
                if ln.lower().startswith("proxy-"):
                    continue
                fwd += ln + "\r\n"
            fwd += "\r\n"
            data = fwd.encode("latin-1")
            if is_tls_client_hello(data):
                await _send_fragmented(remote_w, data)
            else:
                remote_w.write(data)
                await remote_w.drain()
        # Resto do corpo do cliente (se houver) vai direto
        async def _client_first() -> None:
            try:
                while True:
                    chunk = await client_r.read(65536)
                    if not chunk:
                        break
                    if is_tls_client_hello(chunk):
                        await _send_fragmented(remote_w, chunk)
                    else:
                        remote_w.write(chunk)
                        await remote_w.drain()
            except (ConnectionError, asyncio.IncompleteReadError):
                pass
            finally:
                try:
                    remote_w.close()
                except Exception:
                    pass
        await asyncio.gather(_pipe(remote_r, client_w), _client_first())
    finally:
        for w in (client_w, remote_w):
            if w is not None:
                try:
                    w.close()
                except Exception:
                    pass


async def _serve(port: int) -> None:
    global _server
    _server = await asyncio.start_server(_handle, "127.0.0.1", port)
    log.info("proxy local em 127.0.0.1:%s", port)
    async with _server:
        await _server.serve_forever()


def start(port: int = 8899) -> None:
    """Sobe proxy em thread daemon (bloqueia só a thread)."""
    global _loop, _thread, _running_port
    with _lock:
        if _thread is not None and _thread.is_alive():
            if _running_port == port:
                return
            stop()
        loop = asyncio.new_event_loop()
        _loop = loop
        _running_port = port

        def _run() -> None:
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_serve(port))
            except OSError as e:
                log.error("proxy não subiu na porta %s: %s", port, e)
            except (RuntimeError, asyncio.CancelledError):
                pass

        _thread = threading.Thread(target=_run, daemon=True, name="proxy-local")
        _thread.start()


def stop() -> None:
    """Para proxy local."""
    global _loop, _thread, _server, _running_port
    with _lock:
        try:
            if _loop is not None and _server is not None:
                _loop.call_soon_threadsafe(_server.close)
        except RuntimeError:
            pass
        _server = None
        _loop = None
        _thread = None
        _running_port = None


def running() -> bool:
    """True se thread do proxy está viva."""
    return _thread is not None and _thread.is_alive()


def port() -> int | None:
    """Porta atual ou None."""
    return _running_port
