from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    CUSTOMER_EDIT_PERMISSION,
    CUSTOMER_FULFILLMENT_VIEW_PERMISSION,
    CUSTOMER_ORDER_IMPORT_PERMISSION,
    CUSTOMER_ORDER_VIEW_PERMISSION,
    CUSTOMER_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import CustomerAddressCreateRequest, CustomerCreateRequest, CustomerUpdateRequest
from ..services.customer_order_service import CustomerOrderService

router = APIRouter(tags=["customer-orders"])


@router.get("/api/customers")
def list_customers(
    search: str | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(CUSTOMER_VIEW_PERMISSION)),
) -> list[dict]:
    return CustomerOrderService().list_customers(search=search, limit=limit)


@router.post("/api/customers")
def create_customer(
    request: CustomerCreateRequest,
    user: AdminUser = Depends(require_permission(CUSTOMER_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    customer_id = CustomerOrderService().create_customer(request)
    return {"customer_id": customer_id}


@router.get("/api/customers/{customer_id}")
def get_customer(
    customer_id: int,
    _user: AdminUser = Depends(require_permission(CUSTOMER_VIEW_PERMISSION)),
) -> dict:
    customer = CustomerOrderService().get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return customer


@router.patch("/api/customers/{customer_id}")
def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    user: AdminUser = Depends(require_permission(CUSTOMER_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    CustomerOrderService().update_customer(customer_id, request)
    return {"customer_id": customer_id}


@router.post("/api/customers/{customer_id}/addresses")
def create_customer_address(
    customer_id: int,
    request: CustomerAddressCreateRequest,
    user: AdminUser = Depends(require_permission(CUSTOMER_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    address_id = CustomerOrderService().create_customer_address(customer_id, request)
    return {"customer_address_id": address_id}


@router.get("/api/customer-orders")
def list_customer_orders(
    status: str | None = None,
    order_no: str | None = None,
    legacy_order_id: int | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(CUSTOMER_ORDER_VIEW_PERMISSION)),
) -> list[dict]:
    return CustomerOrderService().list_customer_orders(
        status=status,
        order_no=order_no,
        legacy_order_id=legacy_order_id,
        limit=limit,
    )


@router.get("/api/customer-orders/{customer_order_id}")
def get_customer_order(
    customer_order_id: int,
    _user: AdminUser = Depends(require_permission(CUSTOMER_ORDER_VIEW_PERMISSION)),
) -> dict:
    order = CustomerOrderService().get_customer_order(customer_order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Customer order not found.")
    return order


@router.post("/api/customer-orders/import-legacy/{legacy_order_id}")
def import_legacy_order(
    legacy_order_id: int,
    user: AdminUser = Depends(require_permission(CUSTOMER_ORDER_IMPORT_PERMISSION)),
) -> dict[str, int]:
    customer_order_id = CustomerOrderService().import_legacy_order(
        legacy_order_id=legacy_order_id,
        created_by=user.username,
    )
    return {"customer_order_id": customer_order_id}


@router.get("/api/customer-orders/{customer_order_id}/fulfillment")
def get_customer_order_fulfillment(
    customer_order_id: int,
    _user: AdminUser = Depends(require_permission(CUSTOMER_FULFILLMENT_VIEW_PERMISSION)),
) -> list[dict]:
    if CustomerOrderService().get_customer_order(customer_order_id) is None:
        raise HTTPException(status_code=404, detail="Customer order not found.")
    return CustomerOrderService().get_fulfillment(customer_order_id)
