import sys
from pathlib import Path
from hashlib import sha256
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag="13508027ed";actor="WR234"+tag;dispatch="RET237.SUP.LOAD:"+tag;base="http://127.0.0.1:8088";p="/api/inventory/supplier-handover";admin=httpx.Client(auth=("admin","admin123"),timeout=40)
def api(h,path,body=None,status=200):
 r=h.request("POST"if body else"GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:3500]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID=:p",p=actor);client=httpx.Client(auth=(actor,q.fetchone()[0]),timeout=40)
 report={"operation_id":"RET237.SUP.DOC:"+tag,"dispatch_operation_id":dispatch,"document_reference":"DEV.SUP.DOC237:"+tag,"document_sha256":sha256(("Own237 software documentary fixture "+tag).encode()).hexdigest(),"receiver_name":"Own237 simulated supplier recipient"}
 recorded=api(client,p+"/record",report);assert not recorded["stock_changed"]and api(client,p+"/record",report)==recorded
 decision={"operation_id":"RET237.SUP.CONFIRM:"+tag,"handover_operation_id":report["operation_id"],"document_reference":"DEV.SC.SUP237:"+tag,"reason":"Own237 independent documentary software fixture; no external provider ACK"}
 api(client,p+"/confirm",decision,403)
 result=api(admin,p+"/confirm",decision);assert result["status"]=="HANDOVER_CONFIRMED"and api(admin,p+"/confirm",decision)==result
 for op in[report["operation_id"],decision["operation_id"]]:
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=op);assert q.fetchone()[0]==0
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:p",p="RETURN237:"+tag);assert q.fetchone()==(0,0)
 q.execute("select TARGET_SYSTEM,STATUS from RRL_EVENT_OUTBOX where CORRELATION_ID=:p and EVENT_TYPE='MARKED_SUPPLIER_RETURN_DISPATCHED'order by TARGET_SYSTEM",p=dispatch);assert q.fetchall()==[("CRPT","PENDING"),("EGAIS","PENDING")]
 print("PASS237 existing marked supplier documentary handover on actual departed33547/separate independent confirm/replay/no second goods/Gov notifications PENDING/no real archive-ACK claim",decision["operation_id"],flush=True)
