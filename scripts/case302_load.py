exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.transport_composition import build_transport_loading
from app.modules.platform.public import read_oracle_json
import httpx,uuid
loading=build_transport_loading()
with httpx.Client(auth=("admin","admin123"),timeout=35)as h:
 for number in [291,292]:
  ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"));p=Path("tmp/context302_"+str(number)+".json");saved=json.loads(p.read_text(encoding="utf-8"));st=saved["prepared"]["shipment_identifier"];lot=saved["prepared"]["pallet_identifier"]
  if "load_result"not in saved:
   r=h.get("http://127.0.0.1:8088/api/outgoing-quality/"+st);assert r.status_code==200,r.text;qc=r.json()
   scans=[]
   if number==292:
    with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
     q=c.cursor();q.execute("select UNIT_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id",lot_id=lot);ids={row[0]for row in q}
    scans=[code for u in ctx["units"]if u["unit_id"]in ids for code in u["codes"]];assert len(scans)==4
   r=h.post("http://127.0.0.1:8088/api/outgoing-quality/"+st+"/scan",json=dict(operation_id="IW302.QC:"+str(number)+":"+ctx["tag"],expected_composition_signature=qc["composition_signature"],error_count=0,scans=scans));assert r.status_code==200,r.text
   preview=loading.preview_single(st);vehicle=json.loads(Path("tmp/context296_"+str(number)+".json").read_text(encoding="utf-8"))["target_vehicle_number"]
   meta=dict(expected_version=preview["expected_version"],expected_composition_signature=preview["composition_signature"],scan_container=lot,scan_cell=ctx["outbound"],
       loading_context=dict(transport_task_id=saved["trip_id"],scan_vehicle=vehicle,scan_dock=ctx["outbound"],measurements=dict(origin="MANUAL_CONFIRMED",content_version=preview["expected_version"],gross_weight_kg="10",width_m="1",depth_m="1",height_m="1.5")))
   with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
    q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
    req=dict(contract_version=2,operation_id="IW302.LOAD.ROLL:"+uuid.uuid4().hex,command_type="LOAD_SHIPMENT",actor="admin",source=dict(pallet_identifier=st),lines=[],units=[],metadata=meta)
    try:
     q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
     if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
     result=read_oracle_json(out.getvalue());c.rollback()
     q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=lot,cell_code=ctx["outbound"]);assert q.fetchone()==(2,0)
     q.execute("select count(*)from RRL_IW_RECOVERY_DISPATCH where RECOVERY_OPERATION_ID=:recovery_id",recovery_id=saved["prepare_body"]["recovery_id"]);assert q.fetchone()==(0,)
    finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
   op="IW302.LOAD:"+str(number)+":"+ctx["tag"];saved["load_result"]=loading.load_single(op,st,meta,"admin");saved["load_operation_id"]=op;saved["load_metadata"]=meta;p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
  assert loading.load_single(saved["load_operation_id"],st,saved["load_metadata"],"admin")==saved["load_result"]
  if "departure_result"not in saved:
   op="IW302.DEPART:"+str(number)+":"+ctx["tag"];saved["departure_operation_id"]=op;saved["departure_result"]=loading.depart(op,saved["trip_id"],"admin");p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
  assert loading.depart(saved["departure_operation_id"],saved["trip_id"],"admin")==saved["departure_result"]
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   q=c.cursor();q.execute("select STATUS,ROOT_UID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op_id",op_id=saved["load_operation_id"]);assert q.fetchone()==("DEPARTED",lot)
   q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=lot);assert q.fetchone()==(0,0)
   q.execute("select count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st_id",st_id=saved["prepared"]["st_id"]);assert q.fetchone()==(0,)
print("PASS302 actual originalQC+LOAD+DEPART found2 ordinary+marked4QR/rollback/replay/no duplicate FF/historyretained")
