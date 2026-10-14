exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from uuid import uuid4
ctx=json.loads(Path("tmp/context632.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def post(kind,metadata,source):
  command={"contract_version":2,"operation_id":"CLEAN633:"+uuid4().hex,"command_type":kind,"actor":"admin","source":source,"lines":[],"units":[],"metadata":metadata}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:wave and RESERVATION_KIND='HARD'and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",wave=ctx["wave"])
 for(rid,)in q.fetchall():post("RESERVATION_RELEASE",{"reason":"Finish own multi-binding fixture"},{"reservation_id":int(rid)})
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED'where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:wave and STATUS not in('DONE','CANCELLED')",wave=ctx["wave"])
  q.execute("update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED'where PICK_WAVE_ID=:wave and STATUS not in('DONE','CANCELLED')",wave=ctx["wave"])
  q.execute("update RRL_PICK_WAVE set STATUS='DONE'where PICK_WAVE_ID=:wave",wave=ctx["wave"])
  q.execute("update RRL_PICK_RESERVATION set RESERVATION_STATUS='RELEASED'where PICK_PLAN_ID in(select PICK_PLAN_ID from RRL_PICK_TASK where PICK_TASK_ID in(select PICK_TASK_ID from RRL_PICK_WAVE_TASK where PICK_WAVE_ID=:wave))and RESERVATION_STATUS='ACTIVE'",wave=ctx["wave"])
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select WARE_ID from RRL_CELLS where CELL=:cell",cell=ctx["source_cell"]);ware=int(q.fetchone()[0])
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 q.execute("select rr.UID_POLETA,rr.CELL,rr.BASE_UOM,rr.STOCK_VERSION from RRL_REMAINS rr join RRL_PALLETS p on p.UID_PALLET=rr.UID_POLETA where p.ARTICUL=:article and rr.REMAIN>0",article=ctx["article"])
 counts=[{"uid":uid,"cell":cell,"article":ctx["article"],"unit":uom,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]}for uid,cell,uom,version in q.fetchall()]
 if counts:post("INVENTORY_COUNT",{"reason":"Finish own multi-binding fixture","counts":counts},{"revision_id":revision})
 ctx["status"]="REBIND_PASS_OWN_CLEANED";Path("tmp/context632.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("PASS633 own stock/reservations cleaned by original core; rebind history retained, no fixture recreation")
