from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    RIGHTS_ADMIN_EDIT_PERMISSION,
    RIGHTS_ADMIN_VIEW_PERMISSION,
    require_permission,
)
from ..oracle_gateway import OracleGateway
from ..schemas import RightsGrantRequest, RightsGroupRequest, RightsUserGroupRequest

router = APIRouter(prefix="/api/admin/rights", tags=["admin-rights"])


@router.get("/users")
def list_users(
    query: str | None = None,
    group_id: str | None = None,
    include_deleted: int = 0,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION)),
) -> list[dict]:
    where = ["(:include_deleted = 1 or nvl(DELETED, 0) = 0)"]
    params: dict = {
        "include_deleted": include_deleted,
        "limit": min(max(limit, 1), 500),
    }
    if query:
        where.append("(lower(ID) like lower(:query) or lower(NAME) like lower(:query))")
        params["query"] = f"%{query}%"
    if group_id:
        where.append("USER_GROUP = :group_id")
        params["group_id"] = group_id
    sql = f"""
        select *
          from (
            select ID, NAME, DELETED, PRAVO_ADMIN_LOGIN, USER_GROUP, WARE_ID, SMENA
              from RUSERS
             where {" and ".join(where)}
             order by ID
          )
         where rownum <= :limit
    """
    return OracleGateway().fetch_all(sql, params)


@router.get("/groups")
def list_groups(
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION)),
) -> list[dict]:
    return OracleGateway().fetch_all(
        """
        select src.ID,
               nvl(max(g.NAME), src.ID) NAME,
               count(distinct r.RIGHT1) RIGHTS_COUNT,
               count(distinct u.ID) USERS_COUNT,
               max(case when g.ID is not null then 1 else 0 end) IN_USER_GROUP
          from (
            select ID from USER_GROUP where ID is not null
            union
            select USER_GROUP ID from RUSERS where USER_GROUP is not null
            union
            select USER_GROUP ID from RIGHTS where USER_GROUP is not null
          ) src
          left join USER_GROUP g on g.ID = src.ID
          left join RIGHTS r on r.USER_GROUP = src.ID
          left join RUSERS u on u.USER_GROUP = src.ID
         group by src.ID
         order by src.ID
        """
    )


@router.post("/groups")
def upsert_group(
    request: RightsGroupRequest,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> dict:
    group_id = normalize_group_id(request.id)
    name = request.name.strip() or group_id
    OracleGateway().execute(
        """
        merge into USER_GROUP d
        using (select :id ID, :name NAME from dual) s
           on (d.ID = s.ID)
         when matched then update set d.NAME = s.NAME
         when not matched then insert (ID, NAME) values (s.ID, s.NAME)
        """,
        {"id": group_id, "name": name},
    )
    return {"id": group_id, "name": name}


@router.get("/groups/{group_id}/rights")
def list_group_rights(
    group_id: str,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION)),
) -> list[dict]:
    return OracleGateway().fetch_all(
        """
        select RIGHT1, USER_GROUP, ID, DESCR
          from RIGHTS
         where USER_GROUP = :group_id
         order by RIGHT1, ID
        """,
        {"group_id": group_id},
    )


@router.post("/groups/{group_id}/rights")
def grant_group_right(
    group_id: str,
    request: RightsGrantRequest,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> dict:
    right_name = normalize_right_name(request.right_name)
    description = request.description
    exists = OracleGateway().fetch_all(
        """
        select ID
          from RIGHTS
         where USER_GROUP = :group_id
           and upper(RIGHT1) = :right_name
        """,
        {"group_id": group_id, "right_name": right_name},
    )
    if exists:
        OracleGateway().execute(
            """
            update RIGHTS
               set DESCR = :description
             where USER_GROUP = :group_id
               and upper(RIGHT1) = :right_name
            """,
            {"group_id": group_id, "right_name": right_name, "description": description},
        )
    else:
        OracleGateway().execute(
            """
            insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
            values (
              :right_name,
              :group_id,
              (select nvl(max(ID), 0) + 1 from RIGHTS),
              :description
            )
            """,
            {"group_id": group_id, "right_name": right_name, "description": description},
        )
    return {"user_group": group_id, "right1": right_name, "descr": description}


@router.delete("/groups/{group_id}/rights/{right_name}")
def revoke_group_right(
    group_id: str,
    right_name: str,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> dict:
    normalized = normalize_right_name(right_name)
    rowcount = OracleGateway().execute(
        """
        delete from RIGHTS
         where USER_GROUP = :group_id
           and upper(RIGHT1) = :right_name
        """,
        {"group_id": group_id, "right_name": normalized},
    )
    return {"user_group": group_id, "right1": normalized, "deleted": rowcount}


@router.put("/users/{user_id}/group")
def update_user_group(
    user_id: str,
    request: RightsUserGroupRequest,
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> dict:
    group_id = normalize_group_id(request.user_group)
    if not legacy_group_exists(group_id):
        raise HTTPException(status_code=404, detail=f"User group not found: {group_id}")
    params = {
        "user_id": user_id,
        "user_group": group_id,
        "pravo_admin_login": request.pravo_admin_login,
    }
    rowcount = OracleGateway().execute(
        """
        update RUSERS
           set USER_GROUP = :user_group,
               PRAVO_ADMIN_LOGIN = nvl(:pravo_admin_login, PRAVO_ADMIN_LOGIN)
         where lower(ID) = lower(:user_id)
        """,
        params,
    )
    if rowcount == 0:
        raise HTTPException(status_code=404, detail=f"User not found: {user_id}")
    return {"user_id": user_id, "user_group": group_id, "updated": rowcount}


def normalize_group_id(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise HTTPException(status_code=400, detail="Group ID is required.")
    if len(normalized) > 15:
        raise HTTPException(status_code=400, detail="Group ID must fit USER_GROUP.ID.")
    return normalized


def legacy_group_exists(group_id: str) -> bool:
    rows = OracleGateway().fetch_all(
        """
        select ID
          from (
            select ID from USER_GROUP where ID = :group_id
            union all
            select USER_GROUP ID from RUSERS where USER_GROUP = :group_id and rownum = 1
            union all
            select USER_GROUP ID from RIGHTS where USER_GROUP = :group_id and rownum = 1
          )
         where rownum = 1
        """,
        {"group_id": group_id},
    )
    return bool(rows)


def normalize_right_name(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise HTTPException(status_code=400, detail="Right name is required.")
    if len(normalized) > 30:
        raise HTTPException(status_code=400, detail="Right name must fit RIGHTS.RIGHT1.")
    return normalized
