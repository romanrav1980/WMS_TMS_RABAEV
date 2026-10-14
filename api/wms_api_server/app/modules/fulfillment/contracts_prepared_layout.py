from typing import Any, Protocol


class PreparedLayoutPort(Protocol):
    def read(self, order: int, actor: str) -> dict[str, Any]: ...
    def preview(self, order: int, row: int, target: int, actor: str) -> dict[str, Any]: ...
    def move(self, order: int, body: dict[str, Any], actor: str) -> dict[str, Any]: ...


def prepared_layout_service() -> PreparedLayoutPort:
    raise RuntimeError("Prepared ST layout service is not wired")
