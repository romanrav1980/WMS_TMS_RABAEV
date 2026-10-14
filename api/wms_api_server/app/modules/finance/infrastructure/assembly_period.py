"""Read actual assembly clocks without interpreting legacy wall timestamps."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse
from .box_assembly_clocks import box_assembly_clocks


def read_assembly_period(gateway: Any, trip: int, ware: int, region: str, actor: str) -> dict[str, Any]:
    with gateway.transaction("Read actual assembly period evidence") as cursor:
        cursor.execute("set transaction read only")
        require_warehouse(cursor, ware, actor, "transport_dispatch_view")
        try:
            cursor.execute("select to_char(systimestamp at time zone (:region),'TZR')from dual",region=region)
            cursor.fetchone()
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0], "code", 0) == 1882:
                raise LogisticsCostError("COST_TIMEZONE_UNKNOWN", "Неизвестный часовой пояс", 422) from exc
            raise
        cursor.execute("""select l.LOAD_OPERATION_ID,l.COMPOSITION_JSON,l.STATUS
            from RRL_TT_HU_LOAD_FACT l join RRL_STOCK_OPERATION op
            on op.OPERATION_ID=l.LOAD_OPERATION_ID and op.STATE='APPLIED'
            where l.TT_ID=:trip and l.WARE_ID=:ware
            order by l.LOAD_OPERATION_ID fetch first 201 rows only""",trip=trip,ware=ware)
        loads=cursor.fetchall()
        if not loads or len(loads)>200:
            raise LogisticsCostError("COST_LOAD_BOUND","Нужны от 1 до 200 фактических мест выбранного склада")
        lines=[]
        for load,composition,status in loads:
            tree=read_oracle_json(composition)
            nodes=tree.get("nodes",[])
            if not 1<=len(nodes)<=200 or len({n.get("uid")for n in nodes})!=len(nodes):
                raise LogisticsCostError("COST_FROZEN_TREE_BOUND","Нужен точный ограниченный архив")
            for clock in box_assembly_clocks(cursor,tree,ware,region):
                if status!="DEPARTED"and clock["state"]=="READY":
                    clock={**clock,"state":"ACTUAL_DEPARTURE_REQUIRED"}
                lines.append({"load_operation_id":load,**clock})
                if len(lines)>10000:
                    raise LogisticsCostError("COST_BOX_BOUND","Не более 10000 физических коробок")
        if len(lines)>10000:
            raise LogisticsCostError("COST_BOX_BOUND","Не более 10000 физических коробок")
        dates=sorted({line["business_date"]for line in lines if line.get("business_date")})
        complete=bool(lines)and all(line["state"]=="READY"for line in lines)
        return {"trip_id":trip,"warehouse_id":ware,"timezone_region":region,"lines":lines,
                "business_dates":dates,"complete":complete,"single_period":complete and len(dates)==1,
                "state":"READY"if complete and len(dates)==1 else "MULTIPLE_PERIODS"if complete else "INCOMPLETE",
                "legacy_wall_dates_reinterpreted":False,"financial_posting_performed":False,
                "timezone_source":"EXPLICIT_READ_REQUEST","consistent_snapshot":True}
