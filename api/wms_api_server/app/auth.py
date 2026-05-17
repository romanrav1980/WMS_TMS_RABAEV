from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import Settings, get_settings
from .oracle_gateway import OracleGateway


ADMIN_LOGIN_PERMISSION = "wms_admin_login"
API_AUDIT_VIEW_PERMISSION = "api_audit_view"
API_AUDIT_REPLAY_PERMISSION = "api_audit_replay"
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
WAREHOUSE_SETTINGS_VIEW_PERMISSION = "warehouse_settings_view"
WAREHOUSE_SETTINGS_EDIT_PERMISSION = "warehouse_settings_edit"

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
