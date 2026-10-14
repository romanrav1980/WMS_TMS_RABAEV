from typing import Any,Protocol


class OrderDeliveryPort(Protocol):
    def get(self,order_id: int,actor: str) -> dict[str,Any]: ...


def order_delivery_service() -> OrderDeliveryPort:
    raise RuntimeError("Order delivery service not wired")
