"""Independent declarations against an immutable review; no stock or day closure."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse
from .day_reconciliation import DayReconciliation
from ..domain.day_review_material import canonical, material


class DayInspections:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def get(self,review: str,actor: str) -> dict:
        with self.gateway.transaction("Frozen review inspection declarations READ ONLY") as cur:
            cur.execute("set transaction read only")
            cur.execute("select WARE_ID,REPORT_JSON,SOURCE_HASH from RRL_DAY_REVIEW where OPERATION_ID=:review_id",review_id=review)
            row=cur.fetchone()
            if row is None:raise LogisticsCostError("DAY_INSPECTION_REVIEW_REQUIRED","Сверка не найдена.",404)
            require_warehouse(cur,row[0],actor,"transport_dispatch_view")
            report=read_oracle_json(row[1])
            cur.execute("select RESULT_JSON,RECORDED_AT from RRL_DAY_INSPECTION where REVIEW_OPERATION_ID=:review_id order by INSPECTION_ROLE",review_id=review)
            rows=[{**read_oracle_json(value),"recorded_at":recorded}for value,recorded in cur]
            paired=len(rows)==2 and len({value["actor"]for value in rows})==2
            declared_empty=paired and all(value["observed_empty"]is True for value in rows)
            source_empty=report.get("shipping_register",{}).get("shipping_zone_empty_confirmed")is True
            return {"review_operation_id":review,"warehouse_id":row[0],"source_hash":row[2],"rows":rows,
                    "paired_independent_declarations":paired,"both_declared_empty":declared_empty,
                    "source_shipping_zone_empty_at_review":source_empty,
                    "shipping_zone_confirmed_for_frozen_review":declared_empty and source_empty,
                    "day_closed":False,"stock_changed":False,"external_obligations_closed":False}

    def resolve(self,operation: str,body: dict,actor: str) -> dict:
        try:
            with self.gateway.transaction("Resolve original shipping inspection operation") as cur:
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_DAY_INSPECT_API.resolve",[actor,operation,canonical(body),result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code in(20882,20886,20863):
                raise LogisticsCostError("DAY_INSPECTION_RESOLVE_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)from exc
            raise

    def record(self,operation: str,body: dict,actor: str) -> dict:
        request=canonical(body)
        try:
            with self.gateway.transaction("Inspection original operation lookup") as cur:
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_DAY_INSPECT_API.lookup",[actor,operation,request,result])
                if result.getvalue() is not None:return read_oracle_json(result.getvalue())
                cur.execute("select WARE_ID,BUSINESS_DATE,TIMEZONE_REGION,SOURCE_HASH from RRL_DAY_REVIEW where OPERATION_ID=:review_id",review_id=body["review_operation_id"])
                ware,business_day,region,source_hash=cur.fetchone()
            report=DayReconciliation(self.gateway).report(ware,business_day.date()if hasattr(business_day,"date")else business_day,region,actor)
            _,current_hash,captured=material(report)
            if current_hash!=source_hash or body["source_hash"]!=source_hash:
                raise LogisticsCostError("DAY_INSPECTION_CURRENT_SOURCE_CHANGED","Перечитайте сверку: факты изменились.",409)
            with self.gateway.transaction("Append independent shipping inspection declaration") as cur:
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_DAY_INSPECT_API.append_inspection",[actor,operation,request,current_hash,captured.isoformat(timespec="microseconds"),result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code in(20882,20886,20863,1):
                raise LogisticsCostError("DAY_INSPECTION_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)from exc
            raise
