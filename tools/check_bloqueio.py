"""Checa se host/porta parece bloqueado (timeout rápido)."""
import socket

TARGETS = [("google.com", 443), ("youtube.com", 443), ("discord.com", 443), ("1.1.1.1", 443)]

def check(host: str, port: int, timeout: float = 3.0) -> bool:
    """True = alcançável, False = possível bloqueio."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def main() -> None:
    for h, p in TARGETS:
        print(f"{h}:{p}", "OK" if check(h, p) else "BLOQUEADO/TIMEOUT")

if __name__ == "__main__":
    main()
