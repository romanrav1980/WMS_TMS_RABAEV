exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from hashlib import sha256
import httpx,copy
ctx=json.loads(Path("tmp/context292.json").read_text(encoding="utf-8"));tag=ctx["tag"];cell="IR292"+tag
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  for code,blocked in [(cell,1),(ctx["outbound"],0)]:
   q.execute("select count(*)from RRL_CELLS where CELL=:cell_code",cell_code=code)
   if not q.fetchone()[0]:q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell_code,:ware,0,0,0,0,0,0,0,0,:blocked,:blocked)",cell_code=code,ware=ctx["target_warehouse"],blocked=blocked)
   q.execute("select count(*)from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code)",cell_code=code)
   if not q.fetchone()[0]:q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell_code=code)
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and UNIT_ID='1'",lot_id=ctx["lot"]);key=q.fetchone()[0]
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()==(6,)
 c.rollback()
 def native(kind,op,metadata,commit=False):
  req={"contract_version":2,"operation_id":op,"command_type":kind,"actor":"admin","source":{"plan_operation_id":ctx["plan_operation_id"]},"lines":[],"units":[],"metadata":metadata}
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req,ensure_ascii=False),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=read_oracle_json(out.getvalue())
   if commit:c.commit()
   return result
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 native("INTERWARE_UNLOAD","IW292.UNLOAD:"+tag,{"scan_pallet":ctx["lot"],"scan_vehicle":"QL"+tag,"scan_dock":ctx["inbound"]},True)
 scans=[{"system_code":x["system_code"],"profile_code":x["profile_code"],"code_hash":sha256(x["code"].encode()).hexdigest()}for x in ctx["units"][0]["codes"]]
 body={"scan_pallet":ctx["lot"],"scan_cell":cell,"scan_article":ctx["barcode"],"article":ctx["article"],"quantity":"1","base_uom":"EA",
  "partial_receipt":True,"unit_keys":[key],"receipt_pallet_identifier":"IP292:"+tag,"gross_weight_kg":"1",
  "discrepancy_reason":"Изолированная приёмка одной маркированной единицы с сохранением двух её кодов","discrepancy_reference":"Own292 selected1 source3 shortage2","unit_scans":scans}
 ctx.update(receive_cell=cell,selected_unit_key=key,receipt_metadata=body,receipt_operation="IW292.RECEIVE:"+tag)
 Path("tmp/context292.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
 missing=copy.deepcopy(body);missing["unit_scans"]=missing["unit_scans"][:1]
 try:native("INTERWARE_RECEIVE","IW292.MISSING:"+tag,missing)
 except oracledb.DatabaseError as e:assert e.args[0].code==20886 and "QUALITY_UNIQUE_UNIT_PROFILE_COVERAGE_REQUIRED"in str(e),str(e)
 else:raise AssertionError("Missing selected profile accepted")
 rolled=native("INTERWARE_RECEIVE","IW292.ROLL:"+tag,body)
 assert rolled["quantity"]=="1"and rolled["short_quantity"]=="2"and rolled["physical_unit_count"]==1,rolled
 q.execute("select CURRENT_UID,CURRENT_CELL,STOCK_STATUS,UNIT_VERSION from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=:unit_key",unit_key=key)
 moved=q.fetchone();assert moved[:3]==(body["receipt_pallet_identifier"],cell,"AVAILABLE")
 q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='ISSUED'",lot_id=ctx["lot"]);assert q.fetchone()==(2,2)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()==(6,)
 c.rollback();q.execute("select count(*)from RRL_PALLETS where UID_PALLET=:lot_id",lot_id=body["receipt_pallet_identifier"]);assert q.fetchone()==(0,)
 q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='ISSUED'",lot_id=ctx["lot"]);assert q.fetchone()==(3,3)
print("ROLLBACK292 selectedmarked1/2profilecodes ->newP1, remaining2issued/all6codesimmutable; missingprofile refused/all effectsrollback restore3/no newcodebirth")
