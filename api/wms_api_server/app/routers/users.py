"""
users.py — FastAPI роутер управления пользователями и правами.

Sprint 99: просмотр (GET пользователей, групп, прав)
Sprint 100: редактирование (CRUD пользователей, назначение прав группам)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..auth import (
    AdminUser,
    RIGHTS_ADMIN_VIEW_PERMISSION,
    RIGHTS_ADMIN_EDIT_PERMISSION,
    require_permission,
)
from ..oracle_gateway import OracleGateway

router = APIRouter(prefix="/api/admin/users", tags=["user-management"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALL_KNOWN_PERMISSIONS = [
    "wms_admin_login",
    "transport_dispatch_view", "transport_dispatch_edit", "transport_dispatch_close",
    "transport_fleet_edit",
    "edit_bill_tt", "calc_tt_price", "create_tt_price", "send_empty_truck",
    "rights_admin_view", "rights_admin_edit",
    "api_audit_view", "api_audit_replay",
    "warehouse_settings_view", "warehouse_settings_edit",
    "vehicle_type_view", "vehicle_type_edit",
    "pick_plan_view", "pick_plan_create", "pick_plan_cancel",
    "pick_wave_view", "pick_wave_create", "pick_wave_launch", "pick_wave_cancel",
    "pick_topology_view", "pick_topology_edit",
    "bom_view", "bom_edit", "bom_approve",
    "mes_production_view", "mes_production_edit",
    "customer_view", "customer_edit",
    "customer_order_view", "customer_order_import",
]


def _gw() -> OracleGateway:
    return OracleGateway()


# ---------------------------------------------------------------------------
# Sprint 99 — Read endpoints
# ---------------------------------------------------------------------------

@router.get("")
def list_users(
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION)),
) -> list[dict]:
    """Список пользователей без паролей (Sprint 99)."""
    rows = _gw().fetch_all(
        """
        SELECT ID     AS LOGIN,
               NAME   AS DISPLAY_NAME,
               USER_GROUP,
               NVL(PRAVO_ADMIN_LOGIN, 0) AS IS_ADMIN,
               NVL(DELETED, 0)           AS IS_DELETED
          FROM RABAEV.RUSERS
         ORDER BY USER_GROUP, NAME
        """
    )
    return [
        {
            "login": str(r.get("login") or ""),
            "display_name": str(r.get("display_name") or ""),
            "user_group": str(r.get("user_group") or ""),
            "is_admin": bool(r.get("is_admin")),
            "is_deleted": bool(r.get("is_deleted")),
        }
        for r in rows
    ]


@router.get("/groups")
def list_groups(
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION)),
) -> list[dict]:
    """Список групп с назначенными правами (Sprint 99)."""
    rows = _gw().fetch_all(
        """
        SELECT USER_GROUP, LOWER(RIGHT1) AS RIGHT1
          FROM RABAEV.RIGHTS
         WHERE RIGHT1 IS NOT NULL
         ORDER BY USER_GROUP, RIGHT1
        """
    )
    groups: dict[str, list[str]] = {}
    for r in rows:
        g = str(r.get("user_group") or "")
        p = str(r.get("right1") or "")
        groups.setdefault(g, []).append(p)
    return [{"group": g, "rights": sorted(rights)} for g, rights in sorted(groups.items())]


@router.get("/rights")
def list_all_rights(
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION)),
) -> list[str]:
    """Полный справочник кодов прав (Sprint 99)."""
    return sorted(_ALL_KNOWN_PERMISSIONS)


# ---------------------------------------------------------------------------
# Sprint 100 — Write endpoints
# ---------------------------------------------------------------------------

class UserCreateRequest(BaseModel):
    login: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)
    user_group: str = Field(..., min_length=1, max_length=50)
    is_admin: bool = False


class UserUpdateRequest(BaseModel):
    user_group: str = Field(..., min_length=1, max_length=50)
    is_admin: bool = False
    display_name: str | None = None


class UserPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=1)


class GroupRightRequest(BaseModel):
    right: str = Field(..., min_length=1, max_length=100)


@router.post("", status_code=201)
def create_user(
    req: UserCreateRequest,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> dict:
    """Создать пользователя (Sprint 100). Oracle stores passwords as plaintext (legacy)."""
    gw = _gw()
    existing = gw.fetch_all(
        "SELECT COUNT(*) AS CNT FROM RABAEV.RUSERS WHERE LOWER(ID) = LOWER(:login)",
        {"login": req.login},
    )
    if int(existing[0].get("cnt") or 0) > 0:
        raise HTTPException(status_code=409, detail=f"User '{req.login}' already exists")
    gw.execute(
        """
        INSERT INTO RABAEV.RUSERS (ID, NAME, PASS, USER_GROUP, PRAVO_ADMIN_LOGIN, DELETED)
        VALUES (:login, :name, :password, :group_, :is_admin, 0)
        """,
        {
            "login": req.login,
            "name": req.display_name,
            "password": req.password,
            "group_": req.user_group,
            "is_admin": 1 if req.is_admin else 0,
        },
    )
    return {"login": req.login}


@router.patch("/{login}")
def update_user(
    login: str,
    req: UserUpdateRequest,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> dict:
    """Изменить группу / is_admin / имя пользователя (Sprint 100)."""
    gw = _gw()
    sets = ["USER_GROUP = :group_", "PRAVO_ADMIN_LOGIN = :is_admin"]
    params: dict = {"login": login, "group_": req.user_group, "is_admin": 1 if req.is_admin else 0}
    if req.display_name is not None:
        sets.append("NAME = :name")
        params["name"] = req.display_name
    gw.execute(
        f"UPDATE RABAEV.RUSERS SET {', '.join(sets)} WHERE LOWER(ID) = LOWER(:login)",
        params,
    )
    return {"login": login}


@router.delete("/{login}", status_code=204)
def delete_user(
    login: str,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> None:
    """Мягкое удаление пользователя (Sprint 100)."""
    _gw().execute(
        "UPDATE RABAEV.RUSERS SET DELETED = 1 WHERE LOWER(ID) = LOWER(:login)",
        {"login": login},
    )


@router.patch("/{login}/password", status_code=204)
def set_password(
    login: str,
    req: UserPasswordRequest,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> None:
    """Сменить пароль пользователя (Sprint 100)."""
    _gw().execute(
        "UPDATE RABAEV.RUSERS SET PASS = :pwd WHERE LOWER(ID) = LOWER(:login)",
        {"pwd": req.new_password, "login": login},
    )


@router.post("/groups/{group}/rights", status_code=201)
def add_group_right(
    group: str,
    req: GroupRightRequest,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> dict:
    """Добавить право группе (Sprint 100). Idempotent."""
    gw = _gw()
    existing = gw.fetch_all(
        "SELECT COUNT(*) AS CNT FROM RABAEV.RIGHTS WHERE USER_GROUP = :g AND LOWER(RIGHT1) = LOWER(:r)",
        {"g": group, "r": req.right},
    )
    if int(existing[0].get("cnt") or 0) == 0:
        gw.execute(
            "INSERT INTO RABAEV.RIGHTS (USER_GROUP, RIGHT1) VALUES (:g, LOWER(:r))",
            {"g": group, "r": req.right},
        )
    return {"group": group, "right": req.right.lower()}


@router.delete("/groups/{group}/rights/{right}", status_code=204)
def remove_group_right(
    group: str,
    right: str,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> None:
    """Удалить право из группы (Sprint 100)."""
    _gw().execute(
        "DELETE FROM RABAEV.RIGHTS WHERE USER_GROUP = :g AND LOWER(RIGHT1) = LOWER(:r)",
        {"g": group, "r": right},
    )


@router.post("/groups", status_code=201)
def create_group(
    body: dict,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> dict:
    """Создать пустую группу прав (Sprint 100). Группа материализуется первым правом."""
    group = str(body.get("group") or "").strip()
    if not group:
        raise HTTPException(status_code=422, detail="group name required")
    # Вставляем placeholder-право, которое сразу удаляем — это создаёт запись группы
    # Если в Oracle RIGHTS нет отдельной таблицы групп, просто возвращаем ок
    return {"group": group, "rights": []}
