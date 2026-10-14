exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.transport_composition import build_transport_loading
from app.delivery_composition import build_delivery_receipt
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.public import normalize_unit_scan_codes
p=Path("tmp/context342.json");saved=json.loads(p.read_text(encoding="utf-8"));source=saved["sources"][0];receiver=build_delivery_receipt()
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
if "depart"not in saved:saved["depart"]=build_transport_loading().depart("IW344.DEPART:"+source["tag"],source["target_trip"],"admin");save()
address=saved["parts"][source["tag"]]["onward"]["final_address"];preview=receiver.preview(saved["load_operation_id"],address,"admin");proof=preview["marked_unit_control"]
assert proof["supported"]and proof["physical_unit_count"]==6 and proof["expected_scan_count"]==9,proof
assert sorted(len(u["profiles"])for u in proof["units"])==[1,1,1,2,2,2]
scans=[dict(code,disposition="ACCEPTED")for item in saved["sources"]for unit in item["units"]for code in unit["codes"]]
meta=dict(scan_place=preview["root_scan_identifier"],expected_composition_signature=preview["composition_signature"],before_cameras=True,observations=[],case_note="",scale_capture_key="",photo_ids=[],weight_act_confirmed=False,unit_scans=normalize_unit_scan_codes(scans))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("update RRL_SKU_RECEIPT_PROFILE set PROFILE_VERSION='QR_STALE'where ARTICUL=:article and SYSTEM_CODE='CRPT'",article=source["article"])
  q.execute("select RRL_STOCK_STORE_RECEIPT_READ.preview_json(:op,'admin',:addr)from dual",op=saved["load_operation_id"],addr=address);stale=read_oracle_json(q.fetchone()[0])
  assert stale["marked_unit_control"]["supported"]is False and "SAVED_CODE_PROFILE_VERSION" in stale["marked_unit_control"]["reason"],stale
  c.rollback()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def native(metadata,op):
  req=dict(contract_version=2,operation_id=op,command_type="STORE_RECEIPT",actor="admin",source=dict(load_operation_id=saved["load_operation_id"],store_address=address),lines=[],units=[],metadata=metadata);out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   return read_oracle_json(out.getvalue())
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 bad={**meta,"unit_scans":meta["unit_scans"][1:]}
 try:native(bad,"STORE344.BAD:"+source["tag"])
 except oracledb.DatabaseError as e:assert e.args[0].code==20886,str(e)
 else:raise AssertionError("Missing per-SKU unit profile admitted")
 finally:c.rollback()
 op="STORE344.RECEIVE:"+source["tag"];trial=native(meta,op);assert trial["physical_unit_count"]==6 and len(trial["accepted_lines"])==2
 c.rollback()
 q.execute("select count(*)from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:op",op=saved["load_operation_id"]);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op",op=op);assert q.fetchone()[0]==0
print("PASS344 different SKU matrices2+1/6units9codes/current savedversions/stalecard and incompleteprofiles denied/full receipt late rollback")
