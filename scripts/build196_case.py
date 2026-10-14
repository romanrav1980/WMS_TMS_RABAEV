from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/picking_plan.py")
out[str(p)]=p.read_text(encoding="utf-8").replace("{20840, 20846, 20850, 20860, 20881, 20886, 20890}","{20840, 20846, 20850, 20860, 20873, 20881, 20886, 20890}")
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py")
out[str(p)]=p.read_text(encoding="utf-8").replace("where CUSTOMER_ORDER_ROW_ID=:p_row and WARE_ID=:p_ware\n                      and STATUS in('ACCEPTED','USED')","where case when STATUS in('ACCEPTED','USED')then CUSTOMER_ORDER_ROW_ID end=:p_row and WARE_ID=:p_ware")
s=Path("scripts/ni042_weight_box_choice_case.py").read_text(encoding="utf-8").replace("QW195","QW196").replace("CASE195.QA","CASE196.QA").replace("WEIGHT195.CHOICE","WEIGHT196.CHOICE").replace("QA195","QA196")
anchor='  r=manager.post(cancel_url,json=cancel_body);assert r.status_code==200,(r.status_code,r.text);cancelled=r.json()'
insert='''  # Original native planner owns the transaction; outer rollback must remove all projections and binding.
  temporary=int(q.callfunc("RRL_PICKING_API.create_plan",oracledb.DB_TYPE_NUMBER,[order,"FEFO","admin"]))
  q.execute("select STATUS,PICK_PLAN_ID from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);assert q.fetchone()==("USED",temporary)
  c.rollback()
  q.execute("select STATUS,PICK_PLAN_ID from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);assert q.fetchone()==("ACCEPTED",None)
  from concurrent.futures import ThreadPoolExecutor
  def create():return PickingService().create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"))
  with ThreadPoolExecutor(max_workers=2)as pool:created=list(pool.map(lambda _:create(),range(2)))
  assert created[0]==created[1],created
  plan=created[0];plans.append(plan)
  q.execute("select STATUS,PICK_PLAN_ID,PICK_PLAN_LINE_ID from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);status,bound,line=q.fetchone();assert status=="USED"and bound==plan
  q.execute("select REQUESTED_QTY,PLANNED_QTY from RRL_PICK_PLAN_LINE where PICK_PLAN_LINE_ID=:p_id",p_id=line);assert q.fetchone()==(10,8)
  q.execute("select QTY,SOURCE_UID,SOURCE_CELL_CODE from RRL_PICK_TASK where PICK_PLAN_LINE_ID=:p_id",p_id=line);assert q.fetchone()==(8,lot,src)
  q.execute("select sum(RESERVED_QTY)from RRL_PICK_RESERVATION where PICK_PLAN_LINE_ID=:p_id and STATUS='ACTIVE'and RESERVATION_LEVEL='SOFT'",p_id=line);assert q.fetchone()[0]==8
  from fastapi import HTTPException
  try:PickingService().create_plan(PickingPlanCreateRequest(customer_order_id=order,plan_strategy="FIFO",created_by="admin"));raise AssertionError("Changed strategy accepted")
  except HTTPException as exc:assert exc.status_code==409,(exc.status_code,exc.detail)
  r=manager.post(cancel_url,json=cancel_body);assert r.status_code==409,(r.status_code,r.text)
  PickingService().cancel_plan(plan,"admin")
  r=manager.post(cancel_url,json=cancel_body);assert r.status_code==200,(r.status_code,r.text);cancelled=r.json()'''
assert anchor in s;s=s.replace(anchor,insert)
# Ensure failed plans are not left reserving the owned source.
s=s.replace("  def physical_keys(uid,cell):","  for plan in plans:\n   PickingService().cancel_plan(plan,\"admin\")\n  def physical_keys(uid,cell):")
s=s.replace("PASS195","PASS196")
out["scripts/ni042_weight_choice_plan_case.py"]=s
print(json.dumps(out,ensure_ascii=True))
