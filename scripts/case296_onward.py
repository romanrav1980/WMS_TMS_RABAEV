exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import assign_sts
from app.transport_composition import build_transport_loading
import httpx
loading=build_transport_loading()
with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
 for number in[291,292]:
  ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"));p=Path("tmp/context296_"+str(number)+".json");saved=json.loads(p.read_text(encoding="utf-8"));onward=saved["onward_result"];st=onward["shipment_identifier"];lot=ctx["receipt_result"]["pallet_identifier"]
  if "load_result"not in saved:
   assign_sts(OracleGateway(),ctx["target_trip"],[onward["st_number"]],"admin")
   r=client.get("http://127.0.0.1:8088/api/outgoing-quality/"+st);assert r.status_code==200,r.text;quality=r.json()
   scans=[]
   if number==292:
    with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
     q=c.cursor();q.execute("select UNIT_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id",lot_id=lot);ids={r[0]for r in q}
    scans=[code for u in ctx["units"]if u["unit_id"]in ids for code in u["codes"]]
    assert len(scans)==2
   r=client.post("http://127.0.0.1:8088/api/outgoing-quality/"+st+"/scan",json=dict(operation_id="IW296.QC:"+str(number)+":"+ctx["tag"],expected_composition_signature=quality["composition_signature"],error_count=0,scans=scans));assert r.status_code==200,r.text
   preview=loading.preview_single(st)
   metadata=dict(expected_version=preview["expected_version"],expected_composition_signature=preview["composition_signature"],scan_container=lot,scan_cell=ctx["outbound"],
      loading_context=dict(transport_task_id=ctx["target_trip"],scan_vehicle=saved["target_vehicle_number"],scan_dock=ctx["outbound"],
       measurements=dict(origin="MANUAL_CONFIRMED",content_version=preview["expected_version"],gross_weight_kg="10",width_m="1",depth_m="1",height_m="1.5")))
   op="IW296.LOAD:"+str(number)+":"+ctx["tag"];saved["load_result"]=loading.load_single(op,st,metadata,"admin");saved["load_body"]=metadata;saved["load_operation_id"]=op;p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
  assert loading.load_single(saved["load_operation_id"],st,saved["load_body"],"admin")==saved["load_result"]
  r=client.get("http://127.0.0.1:8088/api/inventory/interwarehouse/trips/"+str(ctx["target_trip"])+"/incoming");assert r.status_code==200,r.text
  incoming=r.json();assert incoming["incoming_ready"]and incoming["plans"][0]["receipt_complete"]==0 and incoming["plans"][0]["shortage_resolved"]==1,incoming
  assert incoming["plans"][0]["quantity_to_load"]=="1"and incoming["plans"][0]["confirmed_short_quantity"]=="2",incoming
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   q=c.cursor();q.execute("select RRL_INTERWARE_DEPART_GATE.promises(:trip_id)from dual",trip_id=ctx["target_trip"]);proof=read_oracle_json(q.fetchone()[0]);assert proof[0]["physically_loaded"],proof
   q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=lot);assert q.fetchone()==(0,0)
print("PASS296 existing accepted1 onward assigned/QC/actualLOAD/P0, marked exact1/two codes, native promise/read readiness accounts confirmedshort2 without fullreceipt")
