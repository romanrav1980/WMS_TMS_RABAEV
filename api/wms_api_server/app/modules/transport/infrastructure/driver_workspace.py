"""Existing trip/operation reads and native fact owner, scoped by current driver binding."""
from datetime import date
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from .trip_edit import trip_error
from ..contracts_plan import TransportPlanError

def rows(cur: Any, maximum: int) -> list[dict[str, Any]]:
    names=[x[0].lower() for x in cur.description]
    values=cur.fetchall()
    if len(values)>maximum:
        raise TransportPlanError("DRIVER_RESULT_BOUND","Слишком много строк. Уточните дату или рейс.",409)
    return [dict(zip(names,row)) for row in values]

class DriverWorkspace:
    def __init__(self, gateway: Any) -> None:
        self.gateway=gateway

    def trips(self, driver: int, day: date, actor: str) -> list[dict[str, Any]]:
        try:
            with self.gateway.transaction("Driver day READ ONLY current binding") as cur:
                cur.execute("set transaction read only")
                cur.callproc("RRL_TT_OPERATION_PLAN_API.assert_driver",[driver,actor])
                cur.execute("""select t.ID TASK_ID,to_char(t.SHIPMENT_DATE,'YYYY-MM-DD HH24:MI:SS') SHIPMENT_DATE,
                    t.TRANSPORT NUM_PLAT,t.TRANSTYPE TRANSPORT_TYPE,t.CONDITION,t.PRIMECHANIE NOTE,nvl(t.PRICE,0)PRICE,
                    (select count(distinct s.ADDR)from RRL_SBORKA_PALLETS s where s.TRANSTASK_ID=t.ID)ST_COUNT,
                    nvl(t.TEMP_WEIGHT,0)WEIGHT_KG,
                    (select to_char(sum(f.GROSS_WEIGHT_KG),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')
                     from RRL_TT_HU_LOAD_FACT f where f.TT_ID=t.ID and f.STATUS in('LOADED','DEPARTED'))LOADED_WEIGHT_KG
                    from RRL_TRANSPORT_TASK t where t.VODITEL_ID=:driver
                    and t.SHIPMENT_DATE>=:day and t.SHIPMENT_DATE<:day+1 and nvl(t.DELETED,0)=0
                    order by t.SHIPMENT_DATE,t.ID fetch first 201 rows only""",driver=driver,day=day)
                return rows(cur,200)
        except oracledb.DatabaseError as exc:
            raise trip_error(exc) from exc

    def details(self, driver: int, trip: int, kind: str, actor: str) -> list[dict[str, Any]]:
        if kind not in {"sts","ops"}:
            raise ValueError("Unsupported driver view")
        try:
            with self.gateway.transaction("Driver trip READ ONLY current binding") as cur:
                cur.execute("set transaction read only")
                cur.callproc("RRL_TT_OPERATION_PLAN_API.assert_driver",[driver,actor])
                cur.execute("select ID from RRL_TRANSPORT_TASK where ID=:trip and VODITEL_ID=:driver and nvl(DELETED,0)=0",trip=trip,driver=driver)
                if cur.fetchone() is None:
                    raise TransportPlanError("DRIVER_TRIP_ASSIGNMENT_REQUIRED","Рейс не назначен этому водителю.",403)
                if kind=="sts":
                    cur.execute("""select ST_NUMBER,ADDR,nvl(ORD,0)ORD,
                        to_char(ZONE_TIME_PLAN_IN,'YYYY-MM-DD HH24:MI:SS') TIME_FROM,
                        to_char(ZONE_TIME_PLAN_OUT,'YYYY-MM-DD HH24:MI:SS') TIME_TO,LOAD_TYPE,count(PALLET_UID)PALLET_COUNT
                        from RRL_SBORKA_PALLETS where TRANSTASK_ID=:trip
                        group by ST_NUMBER,ADDR,ORD,ZONE_TIME_PLAN_IN,ZONE_TIME_PLAN_OUT,LOAD_TYPE
                        order by ORD nulls last,ST_NUMBER,ADDR fetch first 501 rows only""",trip=trip)
                else:
                    cur.execute("""select ID OP_ID,OPERATION_CODE,ORD,
                        to_char(PLAN_START,'YYYY-MM-DD HH24:MI:SS')PLAN_START,to_char(PLAN_END,'YYYY-MM-DD HH24:MI:SS')PLAN_END,
                        to_char(FACT_START,'YYYY-MM-DD HH24:MI:SS')FACT_START,to_char(FACT_END,'YYYY-MM-DD HH24:MI:SS')FACT_END,NOTE,
                        case when FACT_END is not null then 'done'when FACT_START is not null then 'in_progress'else 'pending'end STATUS
                        from RRL_TT_OPERATIONS where TT_ID=:trip order by ORD,ID fetch first 501 rows only""",trip=trip)
                return rows(cur,500)
        except oracledb.DatabaseError as exc:
            raise trip_error(exc) from exc

    def mark(self, driver: int, operation: int, action: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Existing driver fact serialized native owner") as cur:
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TT_OPERATION_PLAN_API.mark_driver_fact",[operation,driver,actor,action,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0],"code",0) in {54,60}:
                raise TransportPlanError("DRIVER_FACT_BUSY","Операция занята. Повторите ту же отметку.",409) from exc
            raise trip_error(exc) from exc
