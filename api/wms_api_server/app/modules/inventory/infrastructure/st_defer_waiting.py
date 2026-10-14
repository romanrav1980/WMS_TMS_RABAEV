import logging
import oracledb
from ....oracle_gateway import OracleGateway
from ...platform.public import read_oracle_json
from ..contracts_waiting_tasks import WaitingTaskError,WaitingTaskRequest

_logger=logging.getLogger(__name__)

class StDeferWaiting:
    def __init__(self,gateway: OracleGateway) -> None:
        self.gateway=gateway

    def plan(self,request: WaitingTaskRequest,actor: str) -> dict:
        try:
            with self.gateway.transaction("Plan existing deferred ST waiting tasks; no stock effect") as cur:
                out=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",[request.operation_id,request.decision_operation_id,actor,out,request.root_identifier])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==20882:status=403
            elif code==1403:status=404
            elif 20800<=code<=20999:status=409
            else:status=503
            if status==503:
                _logger.warning("ST waiting plan unconfirmed operation=%s oracle_code=%s",request.operation_id,code or None)
            if code==20886 and "DEFER_WAIT_ROOT_SELECTION_REQUIRED" in str(exc):
                raise WaitingTaskError("ST_WAITING_ROOT_SELECTION_REQUIRED","Choose a top place before planning",409) from exc
            raise WaitingTaskError("ST_WAITING_PLAN_REJECTED" if status!=503 else "ST_WAITING_PLAN_UNCONFIRMED",str(exc.args[0]).split("\n",1)[0] if status!=503 else "Repeat the original operation and decision",status) from exc

    def read(self,decision: str,actor: str,after: int,limit: int) -> dict:
        with self.gateway.transaction("Current waiting tasks READ ONLY bounded warehouse scope") as cur:
            cur.execute("set transaction read only")
            cur.execute("""select d.WARE_ID,d.ST_NUMBER,s.DEFER_WAIT_CELL
                from RRL_ST_DEFER_DECISION d join RUSERS u on u.ID=:actor
                left join RRL_RECEIPT_WARE_SETTINGS s on s.WARE_ID=d.WARE_ID
                where d.OPERATION_ID=:decision and nvl(u.DELETED,0)=0
                and RRL_HAS_WRIGHT(u.ID,'warehouse_task_view')=1
                and(u.WARE_ID=d.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')""",
                {"actor":actor,"decision":decision})
            header=cur.fetchone()
            if header is None:
                raise WaitingTaskError("ST_WAITING_DECISION_OUTSIDE_SCOPE","Decision not found in the current warehouse scope",404)
            cur.execute("""select p.TASK_ID,p.UID_PALLET,p.FROM_CELL,p.TARGET_CELL,p.BASE_QTY,p.BASE_UOM,
                t.STATUS,t.FACT_QTY,s.SYNC_STATUS
                from RRL_ST_DEFER_WAIT_RUN r join RRL_ST_DEFER_WAIT_PLAN p on p.PLAN_OPERATION_ID=r.OPERATION_ID
                join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID
                left join RRL_WAREHOUSE_TASK_SYNC s on s.TASK_ID=p.TASK_ID
                where r.DECISION_OPERATION_ID=:decision and p.TASK_ID>:after_id
                order by p.TASK_ID fetch first :max_rows rows only""",
                {"decision":decision,"after_id":after,"max_rows":limit+1})
            rows=cur.fetchall()
            tasks=[dict(zip(("task_id","pallet_identifier","from_cell","to_cell","quantity","base_uom","status","fact_quantity","sync_status"),row)) for row in rows[:limit]]
            for task in tasks:
                for key in ("quantity","fact_quantity"):
                    if task[key] is not None:task[key]=str(task[key])
            places_out=cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_ST_DEFER_WAIT_API.read_places",[decision,actor,places_out])
            places=read_oracle_json(places_out.getvalue())
            return {"available_places":places.get("places",[]),"selection_required":places.get("selection_required",False),
                    "places_unavailable_reason":places.get("unavailable_reason"),
                    "decision_operation_id":decision,"warehouse_id":header[0],"st_number":header[1],"waiting_cell":header[2],
                    "tasks":tasks,"has_more":len(rows)>limit,"next_after_task_id":tasks[-1]["task_id"] if len(rows)>limit else None}
