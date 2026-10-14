exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.interwarehouse_scans import normalize_interwarehouse_scans
import httpx
path=Path("tmp/context310.json");ctx=json.loads(path.read_text(encoding="utf-8"));cell="IR310"+ctx["tag"];operation="IW310.RECEIVE:"+ctx["tag"]
client=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088/api/inventory/interwarehouse"
if "receipt_result"in ctx:raise SystemExit("310 already received; saved exact HTTP replay only")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("select count(*)from RRL_CELLS where CELL=:cell_code",cell_code=cell)
  if not q.fetchone()[0]:
   q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell_code,:ware,0,0,0,0,0,0,0,0,1,1)",cell_code=cell,ware=ctx["target_warehouse"])
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell_code=cell)
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 r=client.post(base+"/unload",json=dict(operation_id="IW310.UNLOAD:"+ctx["tag"],plan_operation_id=ctx["plan_operation_id"],scan_pallet=ctx["lot"],scan_vehicle="QL"+ctx["tag"],scan_dock=ctx["inbound"]));assert r.status_code==200,r.text
 body=dict(operation_id=operation,plan_operation_id=ctx["plan_operation_id"],scan_pallet=ctx["lot"],scan_cell=cell,scan_article=ctx["barcode"],article=ctx["article"],quantity="3",base_uom="EA",aggregation_scans=ctx["aggregations"])
 metadata=normalize_interwarehouse_scans({k:v for k,v in body.items()if k not in["operation_id","plan_operation_id"]})
 def native(meta,op):
  req=dict(contract_version=2,operation_id=op,command_type="INTERWARE_RECEIVE",actor="admin",source=dict(plan_operation_id=ctx["plan_operation_id"]),lines=[],units=[],metadata=meta)
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   return read_oracle_json(out.getvalue())
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 invalid_cases=[
  {**metadata,"aggregation_scans":metadata["aggregation_scans"][:-1]},
  {**metadata,"aggregation_scans":metadata["aggregation_scans"]+[metadata["aggregation_scans"][0]]},
  {**metadata,"aggregation_scans":[{**metadata["aggregation_scans"][0],"code_hash":"f"*64},metadata["aggregation_scans"][1]]}]
 for i,invalid in enumerate(invalid_cases):
  try:native(invalid,"IW310.BAD"+str(i)+":"+ctx["tag"])
  except oracledb.DatabaseError as e:assert e.args[0].code in[20871,20886,20887],str(e)
  else:raise AssertionError("Invalid aggregate admitted")
  finally:c.rollback()
 trial=native(metadata,operation)
 assert trial["physical_unit_count"]==3,trial
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()==(3,0)
 c.rollback()
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()==(0,0)
 q.execute("select count(*)from RRL_INTERWARE_RECEIPT where OPERATION_ID=:op",op=operation);assert q.fetchone()[0]==0;c.rollback()
 r=client.post(base+"/receive",json=body);assert r.status_code==200,r.text;result=r.json()
 assert result["physical_unit_count"]==3 and result["regulatory_ack_verified"]is False,result
 repeat=client.post(base+"/receive",json=body);assert repeat.status_code==200 and repeat.json()==result,repeat.text
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()==(3,0)
 q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and CURRENT_CELL=:cell_code and STOCK_STATUS='AVAILABLE'",lot_id=ctx["lot"],cell_code=cell);assert q.fetchone()[0]==3
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()[0]==6
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
 ctx.update(receive_cell=cell,receipt_body=body,receipt_result=result,receipt_operation=operation)
 path.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("PASS310 nested sender graph4nodes/scans2 -> native receive3units/6oldcodes/P3H0; missing/duplicate/unknown aggregates denied; late rollback/replay; no rebirth/governmentACK; protected20-20")
