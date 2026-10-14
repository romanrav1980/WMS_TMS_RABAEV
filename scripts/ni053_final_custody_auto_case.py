import sys,json
from pathlib import Path
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
raw=Path("tmp/source232.log").read_text(encoding="utf-16")
ctx=json.loads(next(x.split("SOURCE232_JSON:",1)[1]for x in raw.splitlines()if "SOURCE232_JSON:"in x))
s=get_settings();uid=ctx["uid"];load=ctx["load"];addr="Own full-pallet ST";op="STORE232.AUTO:"+ctx["tag"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 with httpx.Client(auth=("admin","admin123"),timeout=40)as h:
  base="http://127.0.0.1:8088/api/delivery/store-receipts"
  r=h.post(base+"/receivers",json={"store_address":addr,"username":"admin"});assert r.status_code==200,(r.status_code,r.text)
  r=h.get(base+"/preview",params={"load_operation_id":load,"store_address":addr});assert r.status_code==200,(r.status_code,r.text);preview=r.json()
  q.execute("select SYSTEM_CODE,PROFILES_JSON,RAW_CODE from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u order by SYSTEM_CODE,CODE_HASH",u=uid);scans=[]
  for system,profiles,code in q.fetchall():
   for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":code.read()if hasattr(code,"read")else code})
  body={"operation_id":op,"load_operation_id":load,"store_address":addr,"scan_place":uid,"expected_composition_signature":preview["composition_signature"],"before_cameras":True,"scans":scans}
  metadata={k:v for k,v in body.items()if k not in("operation_id","load_operation_id","store_address","scans")};metadata["unit_scans"]=normalize_unit_scan_codes(scans)
  command={"contract_version":2,"operation_id":op+".ROLLBACK","command_type":"STORE_RECEIPT","actor":"admin","source":{"load_operation_id":load,"store_address":addr},"lines":[],"units":[],"metadata":metadata};out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select count(*)from RRL_STORE_LOAD_CUSTODY where OPERATION_ID=:p",p=command["operation_id"]);assert q.fetchone()[0]==1
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select CUSTODY_RELEASED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=load);assert q.fetchone()[0]is None
  r=h.post(base+"/confirm",json=body);assert r.status_code==200,(r.status_code,r.text);result=r.json();assert result["load_custody_released"]is True
  assert h.post(base+"/confirm",json=body).json()==result
 q.execute("select count(*)from RRL_STORE_LOAD_CUSTODY where OPERATION_ID=:p and RECEIPT_OPERATION_ID=:p and LOAD_OPERATION_ID=:l",p=op,l=load);assert q.fetchone()[0]==1
 q.execute("select STATUS,CUSTODY_RELEASE_OPERATION_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=load);assert q.fetchone()==("DEPARTED",op)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=op);assert q.fetchone()[0]==0
 q.execute("select count(*),min(UNIT_VERSION),max(UNIT_VERSION)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'",u=uid);assert q.fetchone()==(3,7,7)
 print("PASS232 automatic full marked receipt3/6QR and custody same TX/native outer rollback/replay/old departure and issued units retained/no second goods",op,ctx["order"],flush=True)
