from typing import Any,Protocol


class SapStoreReturnsPort(Protocol):
    def receive(self,raw: bytes,actor: str) -> dict[str,Any]: ...


def sap_store_returns_service() -> SapStoreReturnsPort:
    raise RuntimeError("SAP store returns not wired")
