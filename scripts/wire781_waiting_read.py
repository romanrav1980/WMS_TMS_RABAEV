from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py");t=p.read_text(encoding="utf-8")
t=t.replace("    def plan(self,request: WaitingTaskRequest,actor: str) -> dict: ...","    def plan(self,request: WaitingTaskRequest,actor: str) -> dict: ...\n    def read(self,decision: str,actor: str,after: int,limit: int) -> dict: ...")
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/st_defer_waiting.py");t=p.read_text(encoding="utf-8")
t+='''
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
            return {"decision_operation_id":decision,"warehouse_id":header[0],"st_number":header[1],"waiting_cell":header[2],
                    "tasks":tasks,"has_more":len(rows)>limit,"next_after_task_id":tasks[-1]["task_id"] if len(rows)>limit else None}
'''
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/api/waiting_task_routes.py");t=p.read_text(encoding="utf-8").replace("APIRouter,Depends,HTTPException","APIRouter,Depends,HTTPException,Query")
t+='''
@router.get("/waiting-tasks")
def read_waiting(decision_operation_id: str=Query(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$"),
                 after_task_id: int=Query(default=0,ge=0),limit: int=Query(default=100,ge=1,le=200),
                 user: AdminUser=Depends(require_permission("warehouse_task_view")),
                 service: WaitingTaskPort=Depends(waiting_task_dependency)) -> dict:
    try:
        return service.read(decision_operation_id,user.username,after_task_id,limit)
    except WaitingTaskError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
'''
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
