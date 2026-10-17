from typing import Any
import oracledb
from ..contracts import LogisticsCostError

def require_warehouse(cursor: Any,ware: int,actor: str,permission: str) -> None:
    try:
        cursor.callproc("RRL_ACCESS_API.assert_allowed",[actor,permission,"WAREHOUSE",str(ware),None])
        cursor.execute("select count(*)from RRL_WARES where ID=:ware",{"ware":ware})
        if cursor.fetchone()[0]!=1: raise LogisticsCostError("COST_WAREHOUSE_FORBIDDEN","Нет полномочий на этот склад",403)
    except oracledb.DatabaseError as error:
        if getattr(error.args[0],"code",0)==20851:
            raise LogisticsCostError("COST_WAREHOUSE_FORBIDDEN","Нет полномочий на этот склад",403) from error
        raise
