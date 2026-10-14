"""Separate short transaction per immutable departed source; no warehouse stock writes."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_forecast import WarehouseForecastError
from .forecast_access import require_forecast_warehouse

class ForecastProjection:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def project_load(self,load_id: str,actor: str) -> dict[str,Any]:
        try:
            with self.gateway.transaction("Actual departure forecast projection")as cur:
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_FORECAST_PROJECTOR.project_load",[load_id,actor,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1403:
                raise WarehouseForecastError("FORECAST_SOURCE_NOT_FOUND","Исходная отгрузка не найдена",404) from exc
            if 20800<=code<=20999:
                raise WarehouseForecastError("FORECAST_SOURCE_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise WarehouseForecastError("FORECAST_PROJECTION_UNCONFIRMED","Повторите материализацию исходного места",503) from exc

    def project(self,ware: int,limit: int,actor: str) -> dict[str,Any]:
        with self.gateway.transaction("Bounded pending forecast sources")as cur:
            require_forecast_warehouse(cur,ware,actor)
            cur.execute("""select f.LOAD_OPERATION_ID from RRL_TT_HU_LOAD_FACT f where f.WARE_ID=:ware and f.STATUS='DEPARTED'
                and f.DEPARTED_AT is not null and not exists(select 1 from RRL_FORECAST_LOAD p where p.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID)
                order by f.DEPARTED_AT,f.LOAD_OPERATION_ID fetch first :row_limit rows only""",ware=ware,row_limit=min(max(limit,1),100))
            ids=[row[0]for row in cur.fetchall()]
        results=[];errors=[]
        for load_id in ids:
            try:
                results.append(self.project_load(load_id,actor))
            except WarehouseForecastError as exc:
                errors.append({"source_load_operation_id":load_id,"code":exc.code,"message":str(exc),"status":exc.status})
        return {"warehouse_id":ware,"sources_seen":len(ids),"projected":results,"errors":errors,"stock_changed":False,"maximum_batch":100}
