exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
import httpx
ctx=json.loads(Path("tmp/context519.json").read_text(encoding="utf-8"));tag=ctx["tag"];load=ctx["load"]
p=Path("tmp/context543.json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else dict(source=ctx)
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with httpx.Client(auth=("admin","admin123"),timeout=35)as api:
 base="http://127.0.0.1:8088/api/delivery/store-receipts"
 def call(method,path,body=None,status=200):
  r=api.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2000]);return r.json()
 address="Own full-pallet ST"
 preview=call("GET","/preview?load_operation_id="+load+"&store_address="+address)
 if "start_body"not in saved:
  assert not preview["already_received"]and preview["unloading"]is None,preview
  saved["start_body"]=dict(operation_id="UNLOAD543.START:"+tag,load_operation_id=load,store_address=address,
      expected_composition_signature=preview["composition_signature"],scan_place=preview["root_scan_identifier"],before_cameras=True);save()
  # Exact root metadata participates in caller rollback, no autocommit.
  trial={**saved["start_body"],"operation_id":"UNLOAD543.TRIAL:"+tag}
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
   q.callproc("RRL_STORE_UNLOAD_API.start_unloading",[json.dumps(trial),"admin",out])
   q.execute("select count(*)from RRL_STORE_UNLOAD_START where OPERATION_ID=:op",op=trial["operation_id"]);assert q.fetchone()[0]==1
   c.rollback()
   q.execute("select count(*)from RRL_STORE_UNLOAD_START where LOAD_OPERATION_ID=:op",op=load);assert q.fetchone()[0]==0
 if "start"not in saved:saved["start"]=call("POST","/unloading/start",saved["start_body"]);save()
 assert call("POST","/unloading/start",saved["start_body"])==saved["start"]
 assert saved["start"]["time_source"]=="SYSTEM_CAPTURED"
 if "receipt_body"not in saved:
  preview=call("GET","/preview?load_operation_id="+load+"&store_address="+address)
  assert preview["unloading"]["operation_id"]==saved["start"]["operation_id"]
  body=dict(operation_id="STORE543:"+tag,load_operation_id=load,store_address=address,scan_place=preview["root_scan_identifier"],
            expected_composition_signature=preview["composition_signature"],before_cameras=True)
  # Once actual work started, a receipt cannot omit the method/loader report.
  call("POST","/confirm",body,status=409)
  details=dict(start_operation_id=saved["start"]["operation_id"],method="MANUAL",rolling_difficult=False,
               loader_present=False,evidence_reference="DEV543.RECEIVER:"+tag)
  call("POST","/confirm",{**body,"unloading":{**details,"method":"ROLL_CAGE","rolling_difficult":True,"loader_present":True}},status=409)
  saved["receipt_body"]={**body,"unloading":details};save()
 if "receipt"not in saved:saved["receipt"]=call("POST","/confirm",saved["receipt_body"]);save()
 assert call("POST","/confirm",saved["receipt_body"])==saved["receipt"]
 state=call("GET","/unloading?load_operation_id="+load+"&store_address="+address)
 assert state["unloading"]["status"]=="COMPLETED"and state["unloading"]["receipt_operation_id"]==saved["receipt_body"]["operation_id"],state
 assert saved["receipt"]["status"]=="ACCEPTED"and saved["receipt"]["warehouse_stock_consumed_again"]is False,saved["receipt"]
 saved["state"]=state;save()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select count(*),sum(ACCEPTED_BASE_QTY)from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:op",op=saved["receipt_body"]["operation_id"])
 assert q.fetchone()==(1,3)
 q.execute("select count(*)from RRL_STORE_UNLOAD_START where LOAD_OPERATION_ID=:op",op=load);assert q.fetchone()[0]==1
 q.execute("select count(*),min(METHOD),min(LOADER_PRESENT)from RRL_STORE_UNLOAD_FACT where LOAD_OPERATION_ID=:op",op=load);assert q.fetchone()==(1,"MANUAL",0)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID in(:start_op,:receipt_op)",start_op=saved["start_body"]["operation_id"],receipt_op=saved["receipt_body"]["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS543 actual retained BOX3 customer accepted3: native system start/rollback/replay, missing finish and forged roller refused, original receipt atomically stores manual method/no loader, completed fact once, goods events0/protected20-20. Receiver attestation, no hardware or legal ACK claim.")
