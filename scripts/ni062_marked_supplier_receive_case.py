import sys,json,copy
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
s=get_settings();tag="13508027ed";pickup="RET237.PICKUP:"+tag;approval="RET237.SUPPLIER:"+tag;uid="RETURN237:"+tag;original="FULL.QA:"+tag;ware=51365792;cell="QS234"+tag;second="QR233"+tag;actor="WR234"+tag
base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=40)
def api(h,method,path,body=None,status=200):
 r=h.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:4000]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 q.execute("select count(*)from RRL_CELLS where CELL=:p",p=second)
 if not q.fetchone()[0]:
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:
   q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:p,:w,0,0,0,0,0,0,0,0,1,1)",p=second,w=ware)
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:p),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",p=second);c.commit()
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 policy=api(admin,"GET",f"/api/inventory/store-returns/warehouses/{ware}/policy")
 if policy["policy_version"]==0:api(admin,"PUT",f"/api/inventory/store-returns/warehouses/{ware}/policy",{"supplier_receive_cell":second,"disposal_receive_cell":cell,"expected_version":0})
 q.execute("select PASS from RUSERS where ID=:p",p=actor);row=q.fetchone()
 if row:secret=row[0]
 else:
  secret=uuid4().hex;q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:p,:s,'Own234 warehouse receiver',:g,:w,0,0)",p=actor,s=secret,g=actor.upper(),w=ware);c.commit()
 api(admin,"POST","/api/admin/rights/groups/"+actor.upper()+"/rights",{"right_name":"warehouse_return_receive","description":"Own234 original marked return receipt"})
 client=httpx.Client(auth=(actor,secret),timeout=40)
 rows=api(client,"GET",f"/api/inventory/store-returns/warehouses/{ware}/pending");row=next(x for x in rows if x["pickup_operation_id"]==pickup)
 assert row["marked_unit_control"]["physical_unit_count"]==1 and row["marked_unit_control"]["expected_scan_count"]==2
 q.execute("select c.SYSTEM_CODE,c.PROFILES_JSON,c.RAW_CODE from RRL_STORE_RETURN_UNIT b join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=b.PHYSICAL_UNIT_KEY join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID where b.APPROVAL_OPERATION_ID=:p order by c.SYSTEM_CODE",p=approval);scans=[]
 for system,profiles,code in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":code.read()if hasattr(code,"read")else code})
 q.execute("select BARCODE_SHT from RRL_ARTICULS where ACTICUL=:a",a=row["article"]);barcode=q.fetchone()[0]
 body={"operation_id":"RET237.RECEIVE:"+tag,"pickup_operation_id":pickup,"scan_pallet":uid,"scan_vehicle":row["vehicle_number"],"scan_cell":cell,"scan_article":barcode,"article":row["article"],"quantity":"1","base_uom":row["base_uom"],"expiry_date":row["expiry_date"],"supplier_batch":"OBSERVED.RET237."+tag,"gross_weight_kg":"2","net_weight_kg":"1.5","scans":scans}
 path="/api/inventory/store-returns/receive"
 api(client,"POST",path,dict(body,operation_id="RET237.MISSING:"+tag,scans=scans[:1]),409)
 api(client,"POST",path,dict(body,operation_id="RET237.DUP:"+tag,scans=[scans[0],scans[0]]),409)
 q.execute("update RUSERS set WARE_ID=1365792 where ID=:p",p=actor);c.commit()
 try:api(client,"POST",path,body,403)
 finally:q.execute("update RUSERS set WARE_ID=:w where ID=:p",w=ware,p=actor);c.commit()
 metadata={k:v for k,v in body.items()if k not in("operation_id","pickup_operation_id","scans")};metadata["unit_scans"]=normalize_unit_scan_codes(scans)
 cmd={"contract_version":2,"operation_id":body["operation_id"]+".ROLLBACK","command_type":"STORE_RETURN_RECEIVE","actor":actor,"source":{"pickup_operation_id":pickup},"lines":[],"units":[],"metadata":metadata};out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(cmd),actor,out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(1,0)
  q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and UID_PALLET=:o and STOCK_STATUS='AVAILABLE'and UNIT_VERSION=11",u=uid,o=original);assert q.fetchone()[0]==1
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_PALLETS where UID_PALLET=:u",u=uid);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'and UNIT_VERSION=10",u=original);assert q.fetchone()[0]==2
 def run(i):
  payload=dict(body,operation_id=body["operation_id"]+str(i))
  with httpx.Client(auth=(actor,secret),timeout=40)as h:return h.post(base+path,json=payload),payload
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(run,[0,1]))
 assert sorted(r.status_code for r,b in results)==[200,409],[(r.status_code,r.text[:3500])for r,b in results]
 saved,winner=next((r.json(),b)for r,b in results if r.status_code==200)
 assert saved["physical_unit_count"]==1 and saved["original_unit_codes_retained"]and not saved["available_for_reservation"]
 assert api(client,"POST",path,winner)==saved
 q.execute("update RUSERS set WARE_ID=1365792 where ID=:p",p=actor);c.commit()
 try:api(client,"POST",path,winner,403)
 finally:q.execute("update RUSERS set WARE_ID=:w where ID=:p",w=ware,p=actor);c.commit()
 assert api(client,"POST",path,winner)==saved
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u and CELL=:p",u=uid,p=cell);assert q.fetchone()==(1,0)
 q.execute("select CURRENT_UID,CURRENT_CELL,STOCK_STATUS,UNIT_VERSION,UID_PALLET from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=(select PHYSICAL_UNIT_KEY from RRL_STORE_RETURN_UNIT where APPROVAL_OPERATION_ID=:p)",p=approval);assert q.fetchone()==(uid,cell,"AVAILABLE",11,original)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p",p=original);assert q.fetchone()[0]==6
 q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p and STOCK_STATUS='ISSUED'and UNIT_VERSION=10",p=original);assert q.fetchone()[0]==1
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=winner["operation_id"]);assert q.fetchone()[0]==1
 q.execute("select BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE from RRL_CELLS where CELL=:p",p=cell);assert q.fetchone()==(1,1)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS237 receiving actual original marked return1/2QR/one original key birth-codes retained/current return UID blocked cell/P1H0/unitAVAILABLE11/other2ISSUED10/one stock event/native rollback/concurrent winner/replay/current warehouse403/protected20-20",winner["operation_id"],flush=True)
