exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
p=Path("tmp/context483.json");saved=json.loads(p.read_text(encoding="utf-8"));tag=saved["tag"];ware=38542432
base="http://127.0.0.1:8088";client=httpx.Client(auth=("admin","admin123"),timeout=40)
def call(method,path,body=None):
 r=client.request(method,base+path,json=body);assert r.status_code==200,(r.status_code,r.text[:2000]);return r.json()
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 if "target_cells"not in saved:
  targets=["QT489S"+tag,"QT489D"+tag]
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:
   for cell in targets:
    q.execute("select count(*)from RRL_CELLS where CELL=:cell",cell=cell)
    if not q.fetchone()[0]:
     q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,0,1,1,1,0,100,0)",cell=cell,ware=ware)
     q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
   c.commit()
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
  policy=call("GET",f"/api/inventory/store-returns/warehouses/{ware}/policy")
  call("PUT",f"/api/inventory/store-return-putaway/warehouses/{ware}/targets",dict(supplier_target_cell=targets[0],disposal_target_cell=targets[1],expected_version=policy["policy_version"]))
  saved["target_cells"]=targets;save()
 for basis in ["REFUSED","DAMAGED"]:
  part=saved[basis]
  if "placement"not in part:
   part["placement"]=call("POST","/api/inventory/store-return-putaway/plan",dict(operation_id="EXRET489.PUT:"+basis+":"+tag,receipt_operation_id=part["receipt"]["operation_id"]));save()
  task=part["placement"]["task_id"];target=part["placement"]["to_cell"]
  if "placement_done"not in part:
   call("POST",f"/api/warehouse-tasks/{task}/assign",dict(assigned_to="admin"));call("POST",f"/api/warehouse-tasks/{task}/start",{})
   body=dict(operation_id="EXRET489.DONE:"+basis+":"+tag,scanned_pallet=part["receipt"]["pallet_identifier"],scanned_from_cell=part["receipt"]["cell"],scanned_to_cell=target,fact_qty="1")
   part["placement_done"]=call("POST",f"/api/warehouse-tasks/{task}/complete",body);part["placement_done_body"]=body;save()
  assert call("POST",f"/api/warehouse-tasks/{task}/complete",part["placement_done_body"])==part["placement_done"]
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=part["receipt"]["pallet_identifier"],cell=target);assert q.fetchone()==(1,0)
  q.execute("select RRL_STOCK_ELIGIBILITY.reason(:p_uid,:cell,:ware,1,null,null,'ALLOCATE')from dual",p_uid=part["receipt"]["pallet_identifier"],cell=target,ware=ware);assert q.fetchone()[0]is not None
 print("PASS489 existing return PUT task each1 same physical keys/two isolated target cells/nonallocatable/replay; no customer credit")
