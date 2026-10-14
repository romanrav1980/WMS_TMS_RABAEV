exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
ctx=json.loads(Path("tmp/context307.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PHYSICAL_UNIT_KEY,UNIT_ID,BASE_QTY,BASE_UOM,CURRENT_CELL from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='ISSUED'",lot_id=ctx["lot"]);rows=q.fetchall()
 assert len(rows)==1,rows
 key,unit_id,quantity,base,cell=rows[0]
 scans=next(u["codes"]for u in ctx["units"]if u["unit_id"]==unit_id)
 domain={"legs":[dict(uid=ctx["lot"],cell=cell,article=ctx["article"],base_uom=base,quantity=format(quantity,"f"),selected_unit_keys=[key])]}
 metadata={"unit_scans":normalize_unit_scan_codes(scans)}
 def validate(wire):
  d=q.var(oracledb.DB_TYPE_CLOB);d.setvalue(0,json.dumps(domain))
  m=q.var(oracledb.DB_TYPE_CLOB);m.setvalue(0,json.dumps(wire))
  n=q.var(oracledb.DB_TYPE_NUMBER);q.callproc("RRL_INTERWARE_MARK_SCAN.validate_scan",[d,m,n]);assert n.getvalue()==1
 for mode in ["UNIT","UNIT_OR_AGGREGATION","BOX","PALLET"]:
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute("update RRL_SKU_RECEIPT_PROFILE set SCAN_MODE=:mode_value where ARTICUL=:article",mode_value=mode,article=ctx["article"])
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
  try:
   if mode in ["UNIT","UNIT_OR_AGGREGATION"]:
    validate(metadata)
    for invalid in [{"unit_scans":metadata["unit_scans"][:-1]},{"unit_scans":metadata["unit_scans"]+[metadata["unit_scans"][0]]}]:
     try:validate(invalid)
     except oracledb.DatabaseError as e:assert e.args[0].code in [20871,20886],str(e)
     else:raise AssertionError("Incomplete/duplicate coverage admitted")
   else:
    try:validate(metadata)
    except oracledb.DatabaseError as e:assert e.args[0].code==20887,str(e)
    else:raise AssertionError("Aggregation-only mode admitted unique-unit input")
  finally:c.rollback()
 q.execute("select SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:article",article=ctx["article"]);assert set(r[0]for r in q)=={"UNIT"}
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_INTERWARE_MARK_SCAN'");assert not q.fetchall()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and SQL_TEXT like 'SELECT COUNT(*) FROM RRL_SKU_RECEIPT_PROFILE WHERE ARTICUL%'and SQL_TEXT like '%UNIT_OR_AGGREGATION%'")
 print("SQL309",q.fetchall())
print("PASS309 UNIT and UNIT_OR_AGGREGATION exact native profile coverage; missing/duplicate rejected; BOX/PALLET unit capture denied; mode updates rolled back; current native VALID; protected20-20")
