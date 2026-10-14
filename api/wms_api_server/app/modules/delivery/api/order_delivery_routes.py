from typing import Any
from fastapi import APIRouter,Depends,HTTPException
from ...platform.public import AdminUser,require_permission
from ..contracts_orders import OrderDeliveryPort,order_delivery_service

router=APIRouter(prefix="/api/customer-orders",tags=["order-delivery-progress"])


@router.get("/{order_id}/delivery")
def delivery(order_id: int,user: AdminUser=Depends(require_permission("customer_fulfillment_view")),
             service: OrderDeliveryPort=Depends(order_delivery_service)) -> dict[str,Any]:
    if order_id<1:
        raise HTTPException(422,"Укажите заказ")
    try:
        return service.get(order_id,user.username)
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc
