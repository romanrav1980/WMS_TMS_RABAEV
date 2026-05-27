from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import Settings, get_settings
from .oracle_gateway import OracleGateway


ADMIN_LOGIN_PERMISSION = "wms_admin_login"
API_AUDIT_VIEW_PERMISSION = "api_audit_view"
API_AUDIT_REPLAY_PERMISSION = "api_audit_replay"
SLOW_SQL_VIEW_PERMISSION = "slow_sql_view"
RIGHTS_ADMIN_VIEW_PERMISSION = "rights_admin_view"
RIGHTS_ADMIN_EDIT_PERMISSION = "rights_admin_edit"
TRACEABILITY_VIEW_PERMISSION = "traceability_view"
EXTERNAL_OUTBOX_VIEW_PERMISSION = "external_outbox_view"
EXTERNAL_OUTBOX_RETRY_PERMISSION = "external_outbox_retry"
BOM_VIEW_PERMISSION = "bom_view"
BOM_EDIT_PERMISSION = "bom_edit"
BOM_APPROVE_PERMISSION = "bom_approve"
BOM_BLOCK_PERMISSION = "bom_block"
BOM_MAKE_PRIMARY_PERMISSION = "bom_make_primary"
BOM_USE_ALTERNATIVE_PERMISSION = "bom_use_alternative"
MES_PRODUCTION_VIEW_PERMISSION = "mes_production_view"
MES_PRODUCTION_EDIT_PERMISSION = "mes_production_edit"
MES_PRODUCTION_COMPLETE_PERMISSION = "mes_production_complete"
MES_WMS_BRIDGE_APPLY_PERMISSION = "mes_wms_bridge_apply"
MES_RAW_SUPPLY_VIEW_PERMISSION = "mes_raw_supply_view"
MES_RAW_SUPPLY_CALCULATE_PERMISSION = "mes_raw_supply_calculate"
MES_RAW_TRANSFER_CREATE_PERMISSION = "mes_raw_transfer_create"
MES_RAW_TRANSFER_CONFIRM_PERMISSION = "mes_raw_transfer_confirm"
MES_RAW_TRANSFER_CANCEL_PERMISSION = "mes_raw_transfer_cancel"
WAREHOUSE_SETTINGS_VIEW_PERMISSION = "warehouse_settings_view"
WAREHOUSE_SETTINGS_EDIT_PERMISSION = "warehouse_settings_edit"
RAW_MATERIAL_VIEW_PERMISSION = "raw_material_view"
RAW_MATERIAL_EDIT_PERMISSION = "raw_material_edit"
RAW_MATERIAL_STOCK_VIEW_PERMISSION = "raw_material_stock_view"
RAW_MATERIAL_EXPORT_PERMISSION = "raw_material_export"
FINISHED_GOODS_VIEW_PERMISSION = "finished_goods_view"
FINISHED_GOODS_EDIT_PERMISSION = "finished_goods_edit"
FINISHED_GOODS_STOCK_VIEW_PERMISSION = "finished_goods_stock_view"
FINISHED_GOODS_BATCH_VIEW_PERMISSION = "finished_goods_batch_view"
FINISHED_GOODS_EXPORT_PERMISSION = "finished_goods_export"
QUALITY_BATCH_VIEW_PERMISSION = "quality_batch_view"
QUALITY_BATCH_EDIT_PERMISSION = "quality_batch_edit"
CUSTOMER_VIEW_PERMISSION = "customer_view"
CUSTOMER_EDIT_PERMISSION = "customer_edit"
CUSTOMER_ORDER_VIEW_PERMISSION = "customer_order_view"
CUSTOMER_ORDER_IMPORT_PERMISSION = "customer_order_import"
CUSTOMER_FULFILLMENT_VIEW_PERMISSION = "customer_fulfillment_view"
CUSTOMER_RULE_VIEW_PERMISSION = "customer_rule_view"
CUSTOMER_RULE_EDIT_PERMISSION = "customer_rule_edit"
VEHICLE_TYPE_VIEW_PERMISSION = "vehicle_type_view"
VEHICLE_TYPE_EDIT_PERMISSION = "vehicle_type_edit"
PICK_PLAN_VIEW_PERMISSION = "pick_plan_view"
PICK_PLAN_CREATE_PERMISSION = "pick_plan_create"
PICK_PLAN_CANCEL_PERMISSION = "pick_plan_cancel"
PICK_RESERVATION_VIEW_PERMISSION = "pick_reservation_view"
PICK_SHORTAGE_VIEW_PERMISSION = "pick_shortage_view"
PICK_TOPOLOGY_VIEW_PERMISSION = "pick_topology_view"
PICK_TOPOLOGY_EDIT_PERMISSION = "pick_topology_edit"
WAREHOUSE_TOPOLOGY_VIEW_PERMISSION = "warehouse_topology_view"
WAREHOUSE_TOPOLOGY_EDIT_PERMISSION = "warehouse_topology_edit"
WAREHOUSE_TOPOLOGY_PUBLISH_PERMISSION = "warehouse_topology_publish"
PICK_ROUTE_ADMIN_VIEW_PERMISSION = "pick_route_admin_view"
PICK_ROUTE_ADMIN_EDIT_PERMISSION = "pick_route_admin_edit"
PICK_ROUTE_ADMIN_PUBLISH_PERMISSION = "pick_route_admin_publish"
PICK_WAVE_VIEW_PERMISSION = "pick_wave_view"
PICK_WAVE_CREATE_PERMISSION = "pick_wave_create"
PICK_WAVE_CALCULATE_PERMISSION = "pick_wave_calculate"
PICK_WAVE_LAUNCH_PERMISSION = "pick_wave_launch"
PICK_WAVE_CANCEL_PERMISSION = "pick_wave_cancel"
PICK_WAVE_RELEASE_RESERVES_PERMISSION = "pick_wave_release_reserves"
PICK_WAVE_AUDIT_VIEW_PERMISSION = "pick_wave_audit_view"
STOCK_RESERVATION_VIEW_PERMISSION = "stock_reservation_view"
STOCK_RESERVATION_EDIT_PERMISSION = "stock_reservation_edit"
WAREHOUSE_TASK_VIEW_PERMISSION = "warehouse_task_view"
WAREHOUSE_TASK_EXECUTE_PERMISSION = "warehouse_task_execute"
RESOURCE_MANAGEMENT_VIEW_PERMISSION = "resource_management_view"
RESOURCE_MANAGEMENT_EDIT_PERMISSION = "resource_management_edit"
RESOURCE_SHIFT_VIEW_PERMISSION = "resource_shift_view"
RESOURCE_SHIFT_EDIT_PERMISSION = "resource_shift_edit"
RESOURCE_SESSION_VIEW_PERMISSION = "resource_session_view"
RESOURCE_SESSION_MANAGE_PERMISSION = "resource_session_manage"
RESOURCE_GANTT_VIEW_PERMISSION = "resource_gantt_view"
RESOURCE_GANTT_REPLAN_PERMISSION = "resource_gantt_replan"
RESOURCE_DISPATCH_MANAGE_PERMISSION = "resource_dispatch_manage"
WAREHOUSE_TASK_FORCE_ASSIGN_PERMISSION = "warehouse_task_force_assign"
CASE_PICK_VIEW_PERMISSION = "case_pick_view"
CASE_PICK_EXECUTE_PERMISSION = "case_pick_execute"
CASE_PICK_MANAGE_PERMISSION = "case_pick_manage"
CASE_PICK_SHORT_APPROVE_PERMISSION = "case_pick_short_approve"
INVENTORY_TASK_VIEW_PERMISSION = "inventory_task_view"
INVENTORY_TASK_EXECUTE_PERMISSION = "inventory_task_execute"
TRANSPORT_DISPATCH_VIEW_PERMISSION = "transport_dispatch_view"
TRANSPORT_DISPATCH_EDIT_PERMISSION = "transport_dispatch_edit"
TRANSPORT_DISPATCH_CLOSE_PERMISSION = "transport_dispatch_close"
BILLING_EDIT_PERMISSION = "edit_bill_tt"
BILLING_CALC_PRICE_PERMISSION = "calc_tt_price"
BILLING_CREATE_PRICE_PERMISSION = "create_tt_price"
TRANSPORT_SEND_EMPTY_TRUCK_PERMISSION = "send_empty_truck"

security = HTTPBasic(auto_error=False)


@dataclass(frozen=True)
class AdminUser:
    username: str
    display_name: str
    user_group: str
    permissions: set[str]


def get_current_admin(
    credentials: HTTPBasicCredentials | None = Depends(security),
    settings: Settings = Depends(get_settings),
) -> AdminUser:
    if not settings.admin_auth_enabled:
        return AdminUser(
            username="debug",
            display_name="Debug Admin",
            user_group="DEBUG",
            permissions={"*"},
        )

    if credentials is None:
        raise_unauthorized()

    user = load_admin_user(credentials.username, credentials.password)
    if user is None:
        raise_unauthorized()
    return user


def require_permission(permission: str):
    def dependency(user: AdminUser = Depends(get_current_admin)) -> AdminUser:
        if "*" not in user.permissions and permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}",
            )
        return user

    return dependency


def serialize_admin_user(user: AdminUser) -> dict:
    return {
        "username": user.username,
        "display_name": user.display_name,
        "user_group": user.user_group,
        "permissions": sorted(user.permissions),
    }


def load_admin_user(username: str, password: str) -> AdminUser | None:
    try:
        rows = OracleGateway().fetch_all(
            """
            select ID, NAME, USER_GROUP, PRAVO_ADMIN_LOGIN
              from RUSERS
             where lower(ID) = lower(:username)
               and PASS = :password
               and nvl(DELETED, 0) = 0
            """,
            {"username": username, "password": password},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Admin auth database is unavailable: {exc}",
        ) from exc

    if not rows:
        return None

    row = rows[0]
    user_group = str(row.get("user_group") or "").strip()
    permissions = {"*"} if user_group.upper() == "GLOBAL_ADMIN" else load_group_permissions(user_group)
    if int(row.get("pravo_admin_login") or 0) == 1:
        permissions.add(ADMIN_LOGIN_PERMISSION)

    return AdminUser(
        username=str(row.get("id") or username),
        display_name=str(row.get("name") or row.get("id") or username),
        user_group=user_group,
        permissions=permissions,
    )


def load_group_permissions(user_group: str) -> set[str]:
    if not user_group:
        return set()
    rows = OracleGateway().fetch_all(
        """
        select lower(RIGHT1) RIGHT1
          from RIGHTS
         where USER_GROUP = :user_group
           and RIGHT1 is not null
        """,
        {"user_group": user_group},
    )
    return {str(row.get("right1")).strip() for row in rows if row.get("right1")}


def raise_unauthorized() -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin login required.",
        headers={"WWW-Authenticate": "Basic"},
    )
