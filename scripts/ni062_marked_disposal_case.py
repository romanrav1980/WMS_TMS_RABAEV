import sys,json
from pathlib import Path
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
s=get_settings();tag="13508027ed";uid="RETURN233:"+tag;receipt="RET234.RECEIVE:"+tag+"1";actor="WR234"+tag;ware=51365792
base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=40);path="/api/inventory/return-disposal"
def api(h,method,p,body=None,status=200):
 r=h.request(method,base+p,json=body);assert r.status_code==status,(r.status_code,r.text[:4000]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000;q.execute("select PASS,USER_GROUP from RUSERS where ID=:p",p=actor);secret,group=q.fetchone();client=httpx.Client(auth=(actor,secret),timeout=40)
 for right in["warehouse_return_dispatch","store_return_approve"]:api(admin,"POST","/api/admin/rights/groups/"+group+"/rights",{"right_name":right,"description":"Own236 exact marked disposal source"})
 q.execute("select CELL,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p and REMAIN=1",p=uid);cell,version=q.fetchone()
 q.execute("select x.SYSTEM_CODE,x.PROFILES_JSON,x.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE x on x.UID_PALLET=u.UID_PALLET and x.UNIT_ID=u.UNIT_ID where u.CURRENT_UID=:p order by x.SYSTEM_CODE",p=uid);scans=[]
 for system,profiles,code in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":code.read()if hasattr(code,"read")else code})
 report={"operation_id":"RET236.REPORT:"+tag,"receipt_operation_id":receipt,"document_reference":"DEV.DISPOSAL236:"+tag,"document_sha256":sha256(("Own software disposal fixture "+tag).encode()).hexdigest(),"reason":"Own236 synthetic disposal act; no physical archive/provider ACK claim"}
 reported=api(client,"POST",path+"/report",report);assert not reported["stock_changed"]
 rows=api(client,"GET",path+f"/warehouses/{ware}");row=next(x for x in rows if x["receipt_operation_id"]==receipt);assert row["marked_unit_control"]["expected_scan_count"]==2
 body={"operation_id":"RET236.DISPOSE:"+tag,"request_operation_id":report["operation_id"],"expected_stock_version":int(version),"scan_pallet":uid,"scan_cell":cell,"decision_reference":"DEV.SC236:"+tag,"scans":scans}
 api(client,"POST",path+"/dispose",body,403)
 api(admin,"POST",path+"/dispose",dict(body,operation_id="RET236.MISSING:"+tag,scans=scans[:1]),409)
 api(admin,"POST",path+"/dispose",dict(body,operation_id="RET236.DUP:"+tag,scans=[scans[0],scans[0]]),409)
 metadata={k:v for k,v in body.items()if k not in("operation_id","scans")};metadata["unit_scans"]=normalize_unit_scan_codes(scans)
 cmd={"contract_version":2,"operation_id":body["operation_id"]+".ROLLBACK","command_type":"STORE_RETURN_DISPOSE","actor":"admin","source":{"request_operation_id":report["operation_id"]},"lines":[],"units":[],"metadata":metadata};out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(cmd),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select count(*)from RRL_EVENT_OUTBOX where CORRELATION_ID=:p and EVENT_TYPE='MARKED_GOODS_DISPOSED'",p=cmd["operation_id"]);assert q.fetchone()[0]==2
  q.execute("select STOCK_STATUS,UNIT_VERSION from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p",p=uid);assert q.fetchone()==("ISSUED",13)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and CELL=:x",p=uid,x=cell);assert q.fetchone()==(1,0)
 q.execute("select count(*)from RRL_EVENT_OUTBOX where CORRELATION_ID=:p",p=cmd["operation_id"]);assert q.fetchone()[0]==0
 def run(i):
  payload=dict(body,operation_id=body["operation_id"]+str(i))
  with httpx.Client(auth=("admin","admin123"),timeout=40)as h:return h.post(base+path+"/dispose",json=payload),payload
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(run,[0,1]))
 assert sorted(r.status_code for r,b in results)==[200,409],[(r.status_code,r.text[:4000])for r,b in results]
 saved,winner=next((r.json(),b)for r,b in results if r.status_code==200)
 assert saved["physical_unit_count"]==1 and saved["regulatory_status"]=="PENDING"and len(saved["regulatory_event_ids"])==2 and not saved["external_regulatory_ack"]
 assert api(admin,"POST",path+"/dispose",winner)==saved
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and CELL=:x",p=uid,x=cell);assert q.fetchone()==(0,0)
 q.execute("select STOCK_STATUS,UNIT_VERSION,UID_PALLET from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p",p=uid);assert q.fetchone()==("ISSUED",13,"FULL.QA:"+tag)
 q.execute("select TARGET_SYSTEM,STATUS,PAYLOAD_JSON from RRL_EVENT_OUTBOX where CORRELATION_ID=:p and EVENT_TYPE='MARKED_GOODS_DISPOSED'order by TARGET_SYSTEM",p=winner["operation_id"]);rows=q.fetchall();assert [(r[0],r[1])for r in rows]==[("CRPT","PENDING"),("EGAIS","PENDING")]
 for system,status,payload in rows:
  value=read_oracle_json(payload);assert value["physical_disposal_recorded"]is True and value["external_ack_verified"]is False and len(value["codes"])==1 and len(value["disposal_units"])==1
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p",p="FULL.QA:"+tag);assert q.fetchone()[0]==6
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=winner["operation_id"]);assert q.fetchone()[0]==1
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS236 original independent disposal act/approved1key2QR/blocked P1->0H0/ISSUED13/same birth codes6/native rollback including Gov2 queues/concurrent winner/replay/SAP pending/CRPT-EGAIS canonical notifications PENDING no ACK/protected20-20",winner["operation_id"],flush=True)
