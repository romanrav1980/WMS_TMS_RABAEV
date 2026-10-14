from typing import Any
from ..contracts_forecast import WarehouseForecastError

def require_forecast_warehouse(cur: Any,ware: int,actor: str) -> None:
    cur.execute("select count(*)from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=:ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')",actor=actor,ware=ware)
    if cur.fetchone()[0]!=1:
        raise WarehouseForecastError("FORECAST_CURRENT_WAREHOUSE_REQUIRED","Требуется актуальная привязка к складу",403)

def forecast_rows(cur: Any) -> list[dict[str,Any]]:
    names=[column[0].lower()for column in cur.description]
    return [dict(zip(names,row))for row in cur.fetchall()]
