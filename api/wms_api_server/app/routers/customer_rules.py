from fastapi import APIRouter, Depends

from ..auth import (
    AdminUser,
    CUSTOMER_RULE_EDIT_PERMISSION,
    CUSTOMER_RULE_VIEW_PERMISSION,
    VEHICLE_TYPE_EDIT_PERMISSION,
    VEHICLE_TYPE_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import (
    CustomerProductRuleCreateRequest,
    CustomerShelfLifeRuleCreateRequest,
    CustomerStackRuleCreateRequest,
    CustomerVehicleRuleCreateRequest,
    VehicleTypeCreateRequest,
)
from ..services.customer_rule_service import CustomerRuleService

router = APIRouter(tags=["customer-rules"])


@router.get("/api/customers/{customer_id}/product-rules")
def list_product_rules(
    customer_id: int,
    _user: AdminUser = Depends(require_permission(CUSTOMER_RULE_VIEW_PERMISSION)),
) -> list[dict]:
    return CustomerRuleService().list_product_rules(customer_id)


@router.post("/api/customers/{customer_id}/product-rules")
def create_product_rule(
    customer_id: int,
    request: CustomerProductRuleCreateRequest,
    user: AdminUser = Depends(require_permission(CUSTOMER_RULE_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    rule_id = CustomerRuleService().create_product_rule(customer_id, request)
    return {"customer_product_rule_id": rule_id}


@router.get("/api/customers/{customer_id}/shelf-life-rules")
def list_shelf_life_rules(
    customer_id: int,
    _user: AdminUser = Depends(require_permission(CUSTOMER_RULE_VIEW_PERMISSION)),
) -> list[dict]:
    return CustomerRuleService().list_shelf_life_rules(customer_id)


@router.post("/api/customers/{customer_id}/shelf-life-rules")
def create_shelf_life_rule(
    customer_id: int,
    request: CustomerShelfLifeRuleCreateRequest,
    user: AdminUser = Depends(require_permission(CUSTOMER_RULE_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    rule_id = CustomerRuleService().create_shelf_life_rule(customer_id, request)
    return {"shelf_life_rule_id": rule_id}


@router.get("/api/customers/{customer_id}/stack-rules")
def list_stack_rules(
    customer_id: int,
    _user: AdminUser = Depends(require_permission(CUSTOMER_RULE_VIEW_PERMISSION)),
) -> list[dict]:
    return CustomerRuleService().list_stack_rules(customer_id)


@router.post("/api/customers/{customer_id}/stack-rules")
def create_stack_rule(
    customer_id: int,
    request: CustomerStackRuleCreateRequest,
    user: AdminUser = Depends(require_permission(CUSTOMER_RULE_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    rule_id = CustomerRuleService().create_stack_rule(customer_id, request)
    return {"stack_rule_id": rule_id}


@router.get("/api/customers/{customer_id}/vehicle-rules")
def list_vehicle_rules(
    customer_id: int,
    _user: AdminUser = Depends(require_permission(CUSTOMER_RULE_VIEW_PERMISSION)),
) -> list[dict]:
    return CustomerRuleService().list_vehicle_rules(customer_id)


@router.post("/api/customers/{customer_id}/vehicle-rules")
def create_vehicle_rule(
    customer_id: int,
    request: CustomerVehicleRuleCreateRequest,
    user: AdminUser = Depends(require_permission(CUSTOMER_RULE_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    rule_id = CustomerRuleService().create_vehicle_rule(customer_id, request)
    return {"customer_vehicle_rule_id": rule_id}


@router.get("/api/vehicle-types")
def list_vehicle_types(
    active_only: int | None = None,
    _user: AdminUser = Depends(require_permission(VEHICLE_TYPE_VIEW_PERMISSION)),
) -> list[dict]:
    return CustomerRuleService().list_vehicle_types(active_only=active_only)


@router.post("/api/vehicle-types")
def create_vehicle_type(
    request: VehicleTypeCreateRequest,
    user: AdminUser = Depends(require_permission(VEHICLE_TYPE_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    vehicle_type_id = CustomerRuleService().create_vehicle_type(request)
    return {"vehicle_type_id": vehicle_type_id}
