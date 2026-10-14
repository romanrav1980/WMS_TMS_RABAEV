exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
import uuid,copy,httpx
ctx=json.loads(Path("tmp/context291.json").read_text(encoding="utf-8"));tag=ctx["tag"]
receive_cell="IR291"+tag
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  for cell,blocked in [(receive_cell,1),(ctx["outbound"],0)]:
   q.execute("select count(*)from RRL_CELLS where CELL=:cell_code",cell_code=cell)
   if not q.fetchone()[0]:
    q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell_code,:ware,0,0,0,0,0,0,0,0,:blocked,:blocked)",cell_code=cell,ware=ctx["target_warehouse"],blocked=blocked)
   q.execute("select count(*)from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code)",cell_code=cell)
   if not q.fetchone()[0]:q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell_code=cell)
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def native(kind,op,metadata,commit=False):
  request={"contract_version":2,"operation_id":op,"command_type":kind,"actor":"admin","source":{"plan_operation_id":ctx["plan_operation_id"]},"lines":[],"units":[],"metadata":metadata}
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(request,ensure_ascii=False),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=read_oracle_json(out.getvalue())
   if commit:c.commit()
   return result
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 unload={"scan_pallet":ctx["lot"],"scan_vehicle":"QL"+tag,"scan_dock":ctx["inbound"]}
 native("INTERWARE_UNLOAD","IW291.UNLOAD:"+tag,unload,True)
 body={"scan_pallet":ctx["lot"],"scan_cell":receive_cell,"scan_article":ctx["barcode"],"article":ctx["article"],"quantity":"1","base_uom":"EA",
  "partial_receipt":True,"receipt_pallet_identifier":"IP291:"+tag,"gross_weight_kg":"1","discrepancy_reason":"Изолированная фактическая приёмка одной единицы; две единицы не предъявлены","discrepancy_reference":"Own291 source3 accepted1 shortage2"}
 ctx["receive_cell"]=receive_cell;ctx["receipt_body"]=body;ctx["receipt_operation"]="IW291.RECEIVE:"+tag
 Path("tmp/context291.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
 rolled=native("INTERWARE_RECEIVE","IW291.ROLL:"+tag,body)
 assert rolled["quantity"]=="1"and rolled["short_quantity"]=="2"and rolled["expected_quantity"]=="3",rolled
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=body["receipt_pallet_identifier"],cell_code=receive_cell);assert q.fetchone()==(1,0)
 c.rollback()
 q.execute("select count(*)from RRL_PALLETS where UID_PALLET=:lot_id",lot_id=body["receipt_pallet_identifier"]);assert q.fetchone()==(0,)
 print("ROLLBACK291 partial1/newpallet/short2 +pallet-stock-receipt-event-outbox rolledback; originaldeclared3 unchanged")
