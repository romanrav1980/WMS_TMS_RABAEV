import sys,json
from pathlib import Path
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag="13508027ed";receipt="RET234.RECEIVE:"+tag+"1";uid="RETURN233:"+tag;source="QR233"+tag;ware=51365792;actor="WR234"+tag;target="QD235"+tag;supplier="QT235"+tag
base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=40)
def api(h,method,path,body=None,status=200):
 r=h.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:3500]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000;q.execute("select PASS,USER_GROUP from RUSERS where ID=:a",a=actor);secret,group=q.fetchone();client=httpx.Client(auth=(actor,secret),timeout=40)
 api(admin,"POST","/api/admin/rights/groups/"+group+"/rights",{"right_name":"warehouse_return_place","description":"Own235 original return placement"})
 for cell in[target,supplier]:
  q.execute("select count(*)from RRL_CELLS where CELL=:p",p=cell)
  if not q.fetchone()[0]:
   q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
   try:
    q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:p,:w,0,0,0,0,1,1,1,0,10,0)",p=cell,w=ware)
    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:p),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",p=cell);c.commit()
   finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 policy=api(admin,"GET",f"/api/inventory/store-returns/warehouses/{ware}/policy")
 api(admin,"PUT",f"/api/inventory/store-return-putaway/warehouses/{ware}/targets",{"supplier_target_cell":supplier,"disposal_target_cell":target,"expected_version":policy["policy_version"]})
 body={"operation_id":"RET235.PLAN:"+tag,"receipt_operation_id":receipt};path="/api/inventory/store-return-putaway/plan"
 planned=api(client,"POST",path,body);task=planned["task_id"]
 assert api(client,"POST",path,body)==planned
 q.execute("update RUSERS set WARE_ID=1365792 where ID=:p",p=actor);c.commit()
 try:api(client,"POST",path,body,403)
 finally:q.execute("update RUSERS set WARE_ID=:w where ID=:p",w=ware,p=actor);c.commit()
 api(admin,"POST",f"/api/warehouse-tasks/{task}/assign",{"assigned_to":"admin"})
 metadata={"fact_qty":"1","scanned_pallet":uid,"scanned_from_cell":source,"scanned_to_cell":target}
 cmd={"contract_version":2,"operation_id":"RET235.COMPLETE:"+tag,"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":metadata};out=q.var(oracledb.DB_TYPE_CLOB)
 def post(command,commit):
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   if commit:c.commit()
   return out.getvalue().read()if hasattr(out.getvalue(),"read")else out.getvalue()
  finally:
   if not commit:c.rollback()
   q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 rollback=dict(cmd,operation_id=cmd["operation_id"]+".ROLLBACK");post(rollback,False)
 q.execute("select CURRENT_CELL,UNIT_VERSION from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p",p=uid);assert q.fetchone()==(source,11)
 result=post(cmd,True);assert post(cmd,True)==result
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p",p=task);assert q.fetchone()[0]=="DONE"
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:p",p=task);assert q.fetchone()[0]=="SYNCED"
 q.execute("select CURRENT_CELL,UNIT_VERSION,UID_PALLET,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p",p=uid);assert q.fetchone()==(target,12,"FULL.QA:"+tag,"AVAILABLE")
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:p",p=uid);assert q.fetchone()==(1,0)
 q.execute("select RRL_STOCK_ELIGIBILITY.reason(:p,:cell,:w,1,null,null,'ALLOCATE')from dual",p=uid,cell=target,w=ware);reason=q.fetchone()[0];assert "BLOCK"in reason,reason
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p",p="FULL.QA:"+tag);assert q.fetchone()[0]==6
 q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:p and EVENT_TYPE='STORE_RETURN_PLACED'and STATUS='PENDING'",p="STORE_RETURN_PLACED:"+str(task));assert q.fetchone()[0]==1
 print("PASS235 original marked return putaway/task",task,"DONE-SYNCED/source0-target1-H0/same birth codes6/AVAILABLE12/cell eligibility BLOCK/outer rollback/replay/current plan WARE403/SAP pending",flush=True)
