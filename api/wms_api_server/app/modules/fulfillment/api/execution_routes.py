from typing import Protocol
from fastapi import APIRouter, Depends, HTTPException
from ...platform.public import AdminUser, require_permission


class OrderExecutionPort(Protocol):
    def get(self, order_id: int, actor: str) -> dict: ...


router = APIRouter(prefix="/api/customer-orders", tags=["customer-order-execution"])


def execution_service() -> OrderExecutionPort:
    raise RuntimeError("Order execution not wired")


@router.get("/{order_id}/execution")
def execution(order_id: int, _user: AdminUser = Depends(require_permission("customer_fulfillment_view")),
              service: OrderExecutionPort = Depends(execution_service)) -> dict:
    try:
        return service.get(order_id, _user.username)
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
