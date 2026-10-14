exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.transport_composition import build_transport_loading
p=Path("tmp/context312.json");ctx=json.loads(p.read_text(encoding="utf-8"));source=ctx["source"];operation="IW312.LOAD:"+source["tag"]
if "load_result"in ctx:raise SystemExit("312 already loaded; exact retained result replay only")
metadata=dict(expected_version=ctx["tree"]["nodes"][0]["version"],scan_container=ctx["root"],scan_cell=source["outbound"],
 loading_context=dict(transport_task_id=source["target_trip"],scan_vehicle="QL"+source["tag"],scan_dock=source["outbound"],
 measurements=dict(origin="MANUAL_CONFIRMED",content_version=ctx["tree"]["nodes"][0]["version"],gross_weight_kg="12",width_m="1",depth_m="1",height_m="1.5")))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 req=dict(contract_version=2,operation_id=operation,command_type="HU_SHIP",actor="admin",source=dict(uid=ctx["root"]),lines=[],units=[],metadata=metadata);out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  trial=read_oracle_json(out.getvalue())
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=source["lot"]);assert q.fetchone()==(0,0)
  q.execute("select count(*)from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=operation);assert q.fetchone()[0]==1
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=source["lot"]);assert q.fetchone()==(3,0)
 q.execute("select count(*)from RRL_INTERWARE_ONWARD_DISPATCH where OPERATION_ID=:op",op=operation);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_WMS_HU_LINK where PARENT_UID in(:top_id,:inner_id)and ACTIVE_FLAG=1",top_id=ctx["root"],inner_id=ctx["inner"]);assert q.fetchone()[0]==2;c.rollback()
loading=build_transport_loading();result=loading.load(operation,ctx["root"],metadata,"admin")
assert loading.load(operation,ctx["root"],metadata,"admin")==result
ctx.update(load_metadata=metadata,load_operation_id=operation,load_result=result);p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ROOT_UID,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=operation);assert q.fetchone()==(ctx["root"],"LOADED")
 q.execute("select count(*),sum(BASE_QTY)from RRL_INTERWARE_ONWARD_DISPATCH where OPERATION_ID=:op",op=operation);assert q.fetchone()==(1,3)
 q.execute("select count(*)from RRL_WMS_HU_LINK where PARENT_UID in(:top_id,:inner_id)and ACTIVE_FLAG=1",top_id=ctx["root"],inner_id=ctx["inner"]);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='ISSUED'",lot_id=source["lot"]);assert q.fetchone()[0]==3
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS312 actual nested TOP/BOX/STOCK3 interwarehouse onwardHU loading/one physicalplace/one dispatch/old3units6codes/P0H0; late rollback restores stock/links; exact replay; original fulfillment retained")
