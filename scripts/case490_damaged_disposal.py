exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
from uuid import uuid4
from hashlib import sha256
from app.modules.platform.public import read_oracle_json
p=Path("tmp/context483.json");saved=json.loads(p.read_text(encoding="utf-8"));part=saved["DAMAGED"];tag=saved["tag"];ware=38542432
base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=40)
def call(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2400]);return r.json()
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();actor="QC490"+tag;group=actor.upper()
 q.execute("select PASS from RUSERS where ID=:actor",actor=actor);row=q.fetchone()
 if row:secret=row[0];q.execute("update RUSERS set DELETED=0 where ID=:actor",actor=actor);c.commit()
 else:
  secret=uuid4().hex;q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:actor,:secret,'Own490 disposal reporter',:grp,:ware,0,0)",actor=actor,secret=secret,grp=group,ware=ware);c.commit()
 call(admin,"POST","/api/admin/rights/groups",dict(id=group,name="Own490 reporter"))
 call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",dict(right_name="warehouse_return_dispatch",description="Own490 synthetic act"))
 uid=part["receipt"]["pallet_identifier"];cell=part["placement"]["to_cell"];scans=part["receipt_body"]["scans"]
 try:
  with httpx.Client(auth=(actor,secret),timeout=40)as controller:
   if "disposal_report"not in part:
    text="DEV490 software scenario: damaged delivery unit physically returned and disposition authorised separately. No actual signed destruction certificate or government ACK."
    document=Path("tmp/DEV490_disposal_act.txt");document.write_text(text,encoding="utf-8")
    body=dict(operation_id="EXRET490.REPORT:"+tag,receipt_operation_id=part["receipt"]["operation_id"],document_reference="DEV490:"+tag,document_sha256=sha256(text.encode()).hexdigest(),reason="Dev damaged-delivery return disposition")
    part["disposal_report"]=call(controller,"POST","/api/inventory/return-disposal/report",body);save()
   if "disposal"not in part:
    q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=uid,cell=cell);version=int(q.fetchone()[0])
    body=dict(operation_id="EXRET490.DISPOSE:"+tag,request_operation_id=part["disposal_report"]["operation_id"],expected_stock_version=version,scan_pallet=uid,scan_cell=cell,decision_reference="DEV490.SC:"+tag,scans=scans)
    call(controller,"POST","/api/inventory/return-disposal/dispose",body,status=403)
    part["disposal"]=call(admin,"POST","/api/inventory/return-disposal/dispose",body);part["disposal_body"]=body;save()
  assert call(admin,"POST","/api/inventory/return-disposal/dispose",part["disposal_body"])==part["disposal"]
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=uid,cell=cell);assert q.fetchone()==(0,0)
  q.execute("select UNIT_DISPOSITION from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op and PHYSICAL_UNIT_KEY=:k",op=saved["receipt"],k=saved["selected"]["DAMAGED"][0]);assert q.fetchone()[0]=="DAMAGED"
  q.execute("select ACCEPTED_BASE_QTY,REFUSED_BASE_QTY,DAMAGED_BASE_QTY from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:op",op=saved["receipt"]);assert q.fetchone()==(3,1,1)
  q.execute("select TARGET_SYSTEM,STATUS from RRL_EVENT_OUTBOX where CORRELATION_ID=:op and EVENT_TYPE='MARKED_GOODS_DISPOSED'order by TARGET_SYSTEM",op=part["disposal_body"]["operation_id"]);assert q.fetchall()==[("CRPT","PENDING"),("EGAIS","PENDING")]
  print("PASS490 damaged1 actual existing disposal with independent reporter/admin decision, P0/same physical key/buyerAccepted3 unchanged, two pending regulatory notifications/no ACK/replay")
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=actor);c.commit()
