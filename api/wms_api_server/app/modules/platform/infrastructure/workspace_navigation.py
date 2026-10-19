"""Per-warehouse native capabilities for navigation, never a replacement for command admission."""
from typing import Any
import oracledb
from .metadata_io import MetadataError, rows

WORKSPACE_READ_PERMISSIONS = {
    "tradecase": "tradecase_view",
    "dispatch": "transport_dispatch_view", "waves": "pick_wave_view", "picking": "case_pick_view",
    "warehouse_tasks": "warehouse_task_view", "resource_timeline": "resource_gantt_view",
    "resource_registry": "resource_management_view", "resource_sessions": "resource_session_view",
}


def capability_columns(cur: Any, actor: str) -> str:
    cur.execute("select RRL_ACCESS_API.is_admin(:actor) from dual", actor=actor)
    if cur.fetchone()[0] == 1:
        return ",".join(("case when exists(select 1 from RRL_TRADE_SITE ts where ts.WARE_ID=w.ID)then 1 else 0 end" if name == "tradecase" else "1") + " " + name for name in WORKSPACE_READ_PERMISSIONS)
    # Candidate permissions only prune impossible checks. Warehouse admission remains native.
    cur.execute("""select distinct rr.PERMISSION from RRL_ACCESS_ROLE_RIGHT rr
        join RRL_ACCESS_ROLE r on r.ROLE_ID=rr.ROLE_ID join RRL_ACCESS_ASSIGNMENT a on a.ROLE_ID=r.ROLE_ID
        where a.USERNAME=:actor and r.ACTIVE=1 and a.REVOKED_AT is null and a.VALID_FROM<=systimestamp
          and(a.VALID_UNTIL is null or a.VALID_UNTIL>systimestamp)""", actor=actor)
    candidates = {row[0] for row in cur.fetchall()}
    legacy = ",".join("RRL_HAS_WRIGHT(:actor,'" + permission + "') " + name
                      for name, permission in WORKSPACE_READ_PERMISSIONS.items())
    cur.execute("select " + legacy + " from dual", actor=actor)
    candidates.update(permission for permission, value in zip(WORKSPACE_READ_PERMISSIONS.values(), cur.fetchone()) if value == 1)
    expressions = []
    for name, permission in WORKSPACE_READ_PERMISSIONS.items():
        decision = "RRL_ACCESS_API.allowed(:actor,'" + permission + "','WAREHOUSE',to_char(w.ID))" if permission in candidates else "0"
        if name == "tradecase":
            decision = "case when exists(select 1 from RRL_TRADE_SITE ts where ts.WARE_ID=w.ID)then " + decision + " else 0 end"
        expressions.append(decision + " " + name)
    return ",".join(expressions)



def read_workspace_navigation(gateway: Any, actor: str, capability: str | None = None) -> dict[str, Any]:
    # Identifiers and permission literals are fixed server constants; actor remains bound.
    if capability not in (None, "tradecase"):
        raise MetadataError("WORKSPACE_CAPABILITY_INVALID", 422)
    visible = "tradecase=1" if capability == "tradecase" else " or ".join(name + "=1" for name in WORKSPACE_READ_PERMISSIONS)
    try:
        with gateway.transaction("Native workspace navigation bounded warehouses") as cur:
            cur.execute("lock table RRL_ACCESS_REV in share mode wait 5")
            cur.execute("select REVISION from RRL_ACCESS_REV where ID=1")
            revision = cur.fetchone()[0]
            columns = capability_columns(cur, actor)
            cur.execute("select * from (select w.ID WAREHOUSE_ID,w.NAME TITLE," + columns +
                        " from RRL_WARES w) where " + visible + " order by WAREHOUSE_ID fetch first 501 rows only",
                        {"actor": actor} if ":actor" in columns else {})
            warehouses = rows(cur)
    except oracledb.DatabaseError as error:
        raise MetadataError("WORKSPACE_NAVIGATION_UNAVAILABLE", 503) from error
    limited = len(warehouses) > 500
    result = []
    for row in warehouses[:500]:
        result.append({"warehouse_id": row["warehouse_id"], "title": row["title"],
                       "capabilities": {name: bool(row[name]) for name in WORKSPACE_READ_PERMISSIONS}})
    return {"username": actor, "access_revision": revision, "warehouses": result, "limit": 500,
            "has_more": limited, "driver_entry": "EXISTING_BOUND_LOGIN", "navigation_only": True}
