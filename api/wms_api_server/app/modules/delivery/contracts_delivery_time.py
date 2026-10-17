from typing import Any, Literal, Protocol


class DeliveryTimePort(Protocol):
    def command(self, kind: Literal["plan_window", "record_arrival"], body: dict[str, Any], actor: str) -> dict[str, Any]: ...
    def read(self, load: str, address: str, actor: str) -> dict[str, Any]: ...
    def report(self, warehouse: int, start: str, finish: str, actor: str) -> dict[str, Any]: ...


def delivery_time_service() -> DeliveryTimePort:
    raise RuntimeError("Delivery time source is not wired")
