exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
ctx_path=Path("tmp/context305.json");ctx=json.loads(ctx_path.read_text(encoding="utf-8"));cell="IR305"+ctx["tag"]
if "receipt_result"in ctx:raise SystemExit("Initial305 receipt alreadyretained; continue loss decisions")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  for cell_code,blocked in [(cell,1),(ctx["outbound"],0)]:
   q.execute("select count(*)from RRL_CELLS where CELL=:cell_code",cell_code=cell_code)
   if not q.fetchone()[0]:q.execute("""insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)
     values(:cell_code,:ware,0,0,0,0,0,0,0,0,:blocked,:blocked)""",cell_code=cell_code,ware=ctx["target_warehouse"],blocked=blocked)
   q.execute("select count(*)from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code)",cell_code=cell_code)
   if not q.fetchone()[0]:q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell_code=cell_code)
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and UNIT_ID='1'",lot_id=ctx["lot"]);key=q.fetchone()[0];c.rollback()
 def command(kind,op,meta):
  req=dict(contract_version=2,operation_id=op,command_type=kind,actor="admin",source=dict(plan_operation_id=ctx["plan_operation_id"]),lines=[],units=[],metadata=meta);out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=read_oracle_json(out.getvalue());c.commit();return result
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 command("INTERWARE_UNLOAD","IW305.UNLOAD:"+ctx["tag"],dict(scan_pallet=ctx["lot"],scan_vehicle="QL"+ctx["tag"],scan_dock=ctx["inbound"]))
 meta=dict(scan_pallet=ctx["lot"],scan_cell=cell,scan_article=ctx["barcode"],article=ctx["article"],quantity="1",base_uom="EA",
  partial_receipt=True,unit_keys=[key],receipt_pallet_identifier="IP305:"+ctx["tag"],gross_weight_kg="1",
  discrepancy_reason="Принята одна из трёх маркированных единиц; две отсутствуют",discrepancy_reference="DEV305:missing2",
  unit_scans=normalize_unit_scan_codes(ctx["units"][0]["codes"]))
 result=command("INTERWARE_RECEIVE","IW305.RECEIVE:"+ctx["tag"],meta)
 assert result["physical_unit_count"]==1 and result["short_quantity"]=="2"
 ctx.update(receive_cell=cell,selected_unit_key=key,receipt_metadata=meta,receipt_result=result,receipt_operation=result["operation_id"])
 ctx_path.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("SOURCE305 initialactualpartial1/marked2codes/source3-frozen6codes/lost2; fresh ownfixture notold292 recreation")
