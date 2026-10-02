"""Diagnóstico de DNS: compara DNS do sistema vs DoH."""
import socket

def main() -> None:
    for host in ["google.com", "youtube.com", "discord.com"]:
        try:
            print(host, "->", socket.gethostbyname(host))
        except Exception as e:
            print(host, "FALHOU:", e)

if __name__ == "__main__":
    main()
