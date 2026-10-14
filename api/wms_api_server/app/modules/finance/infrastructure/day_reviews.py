"""Immutable review of a captured reconciliation; no operational closure or quantity effect."""
from datetime import date, datetime
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .day_reconciliation import DayReconciliation
from ..domain.day_review_material import canonical, material
from .cost_access import require_warehouse

class DayReviews:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway
        self.reconciliation=DayReconciliation(gateway)

    def resolve_inspection(self,operation: str,body: dict,actor: str) -> dict:
        from .day_inspections import DayInspections
        return DayInspections(self.gateway).resolve(operation,body,actor)

    def inspection(self,review: str,actor: str) -> dict:
        from .day_inspections import DayInspections
        return DayInspections(self.gateway).get(review,actor)

    def inspect(self,operation: str,body: dict,actor: str) -> dict:
        from .day_inspections import DayInspections
        return DayInspections(self.gateway).record(operation,body,actor)

    def shipping_register(self,ware: int,day: date,after: int,limit: int,actor: str) -> dict:
        from .shipping_register import report
        return report(self.gateway,ware,day,after,limit,actor)

    def history(self,ware: int,day: date,region: str,after: int,limit: int,actor: str) -> dict:
        from .day_review_history import history
        return history(self.gateway,ware,day,region,after,limit,actor)

    def get(self,operation: str,actor: str) -> dict:
        from .day_review_history import detail
        return detail(self.gateway,operation,actor)

    def context(self,ware: int,day: date,region: str,actor: str) -> dict:
        report=self.reconciliation.report(ware,day,region,actor)
        _,source_hash,_=material(report)
        with self.gateway.transaction("Current reconciliation review version READ ONLY") as cur:
            cur.execute("set transaction read only")
            require_warehouse(cur,ware,actor,"transport_dispatch_view")
            result=cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_DAY_REVIEW_API.context",[ware,day,region,actor,result])
            version=read_oracle_json(result.getvalue())
        return {**version,"source_hash":source_hash,"report":report,"snapshot_scope":"CAPTURED_REPORT_NOT_CURRENT_CLOSURE"}

    def resolve(self,operation: str,body: dict,actor: str) -> dict:
        try:
            with self.gateway.transaction("Resolve review outcome after original operation lock") as cur:
                require_warehouse(cur,body["warehouse_id"],actor,"transport_dispatch_edit")
                payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,canonical(body))
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_DAY_REVIEW_API.resolve",[actor,operation,payload,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code in (20882,20886):
                raise LogisticsCostError("DAY_REVIEW_RESOLVE_CONFLICT",str(exc),403 if code==20882 else 409) from exc
            raise

    def record(self,operation: str,body: dict,actor: str) -> dict:
        request=canonical(body)
        try:
            with self.gateway.transaction("Reconciliation review exact operation replay") as cur:
                require_warehouse(cur,body["warehouse_id"],actor,"transport_dispatch_edit")
                result=cur.var(oracledb.DB_TYPE_CLOB);payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,request)
                cur.callproc("RRL_DAY_REVIEW_API.lookup",[actor,operation,payload,result])
                if result.getvalue() is not None:
                    return read_oracle_json(result.getvalue())
            report=self.reconciliation.report(body["warehouse_id"],date.fromisoformat(body["business_date"]),body["timezone_region"],actor)
            raw,current_hash,captured=material(report)
            if current_hash!=body["source_hash"]:
                raise LogisticsCostError("DAY_REVIEW_SOURCE_CHANGED","Факты или открытые обязательства изменились. Перечитайте сверку.",409)
            with self.gateway.transaction("Append captured reconciliation review") as cur:
                require_warehouse(cur,body["warehouse_id"],actor,"transport_dispatch_edit")
                payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,request)
                capture=cur.var(oracledb.DB_TYPE_CLOB);capture.setvalue(0,raw)
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_DAY_REVIEW_API.append_review",[actor,operation,payload,capture,captured,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==20882:
                raise LogisticsCostError("DAY_REVIEW_FORBIDDEN","Нет действующих полномочий на склад.",403) from exc
            if code in (20886,20863,1):
                raise LogisticsCostError("DAY_REVIEW_CONFLICT",str(exc),409) from exc
            raise
