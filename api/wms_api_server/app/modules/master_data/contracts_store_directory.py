from typing import Any, Protocol


class StoreDirectoryPort(Protocol):
    """Справочник магазинов (адресатов доставки): поиск и карточка из существующих источников, только чтение."""

    def search(self, query: str | None, after: str | None, limit: int) -> dict[str, Any]: ...
    def card(self, address: str, actor: str) -> dict[str, Any] | None: ...


def store_directory_service() -> StoreDirectoryPort:
    raise RuntimeError("Store directory service not wired")
