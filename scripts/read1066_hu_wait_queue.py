exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.services.warehouse_task_service import WarehouseTaskService
from app.oracle_gateway import OracleGateway
svc=WarehouseTaskService(OracleGateway())
rows=svc.list_tasks(status="DONE",queue_group="DEFER_WAITING",limit=500)
task=next(x for x in rows if x["task_id"]==1149)
assert task["unit_code"]=="HU"and task["source_doc_type"]=="WAREHOUSE_HU"and task["wait_st_number"]=="MULTI987:4bb85f1f15"
assert task["wait_decision_operation_id"]=="DEC987:4bb85f1f15"and task["wait_target_tt_id"]==33635
detail=svc.get_task_or_404(1149);assert detail["wait_plan_operation_id"]=="HU1057.PLAN:4bb85f1f15"
# Exact source filters must stay exact even within the family.
old=svc.list_tasks(status="DONE",queue_group="DEFER_WAITING",source_doc_type="ST_DEFER_CASE",limit=500)
assert all(x["source_doc_type"]=="ST_DEFER_CASE"for x in old)and all(x["task_id"]!=1149 for x in old)
flat=svc.get_task_or_404(1080);assert flat["source_doc_type"]=="ST_DEFER"and flat["fact_qty_exact"]=="3"
Path("tmp/read1066_hu_wait_queue.json").write_text(json.dumps({"newtask":task,"detail":detail,"oldflat":flat,"exact_case_filter_count":len(old)},indent=2,default=str),encoding="utf-8")
print("PASS1066 family includes original1HU/20EA; exact ST_DEFER_CASE filter retained; current detail decision/TT; protectedflat1080 fact3")
