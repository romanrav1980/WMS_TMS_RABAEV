"""One original session read model, scoped before ordering and row limit."""
from typing import Any
import oracledb
from ....db import rows_as_dicts
from ..contracts_session_read import ResourceReadError

SESSION_SQL = """select * from (
    select s.SESSION_ID,s.SHIFT_ID,s.RESOURCE_ID,r.WARE_ID,r.RESOURCE_CODE,r.RESOURCE_NAME,r.RESOURCE_TYPE,
           s.EQUIPMENT_ID,e.EQUIPMENT_CODE,s.OPERATOR_USER_ID,s.LOGIN_AT,s.LOGOUT_AT,s.STATUS,s.CURRENT_TASK_ID,
           s.LAST_HEARTBEAT_AT,s.TERMINAL_ID,s.ZONE_CODE,s.CREATED_BY,s.CLOSED_BY
    from RRL_RESOURCE_SESSION s join RRL_RESOURCE r on r.RESOURCE_ID=s.RESOURCE_ID
    left join RRL_RESOURCE_EQUIPMENT e on e.EQUIPMENT_ID=s.EQUIPMENT_ID
    {where_sql} order by s.LOGIN_AT desc,s.SESSION_ID desc)where rownum<=:limit"""


def list_session_rows(gateway: Any, session_id: int | None, shift_id: int | None, resource_id: int | None,
                      status: str | None, limit: int, warehouse: int | None, actor: str | None) -> list[dict[str, Any]]:
    conditions, params = [], {"limit": min(max(limit, 1), 500)}
    for key, value, expression in (("session_id", session_id, "s.SESSION_ID"), ("shift_id", shift_id, "s.SHIFT_ID"),
                                    ("resource_id", resource_id, "s.RESOURCE_ID"), ("ware", warehouse, "r.WARE_ID")):
        if value is not None:
            conditions.append(expression + "=:" + key)
            params[key] = value
    if status:
        conditions.append("s.STATUS=:status")
        params["status"] = status.upper()
    if actor is not None:
        conditions.append("RRL_ACCESS_API.allowed(:actor,'resource_session_view','WAREHOUSE',to_char(r.WARE_ID),s.OPERATOR_USER_ID)=1")
        params["actor"] = actor
    sql = SESSION_SQL.format(where_sql="where " + " and ".join(conditions) if conditions else "")
    if actor is None:
        return gateway.fetch_all(sql, params)
    try:
        with gateway.transaction("Resource sessions native scoped read") as cur:
            cur.execute("lock table RRL_ACCESS_REV in share mode wait 5")
            cur.execute("""select count(*) from RUSERS u where ID=:actor and nvl(DELETED,0)=0 and
                exists(select 1 from RRL_WARES w where RRL_ACCESS_API.allowed(:actor,'resource_session_view','WAREHOUSE',to_char(w.ID),:actor)=1)""", actor=actor)
            if cur.fetchone()[0] != 1:
                raise ResourceReadError("RESOURCE_SESSION_SCOPED_VIEW_REQUIRED")
            if warehouse is not None:
                cur.execute("select RRL_ACCESS_API.allowed(:actor,'resource_session_view','WAREHOUSE',:ware,:actor) from dual",
                            actor=actor, ware=str(warehouse))
                if cur.fetchone()[0] != 1:
                    raise ResourceReadError("RESOURCE_SESSION_WAREHOUSE_DENIED")
            cur.execute(sql, params)
            return rows_as_dicts(cur)
    except oracledb.DatabaseError as error:
        raise ResourceReadError("RESOURCE_SESSION_READ_UNAVAILABLE", 503) from error
