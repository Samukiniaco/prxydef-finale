"""Base de provedores (interface futura p/ VPS). Desligado por padrão."""

class Provider:
    """Interface que todo provedor (VPS) deve implementar."""
    name = "base"
    def connect(self) -> None:
        raise NotImplementedError
    def disconnect(self) -> None:
        raise NotImplementedError
