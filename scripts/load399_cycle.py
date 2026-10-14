exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.transport_composition import build_transport_loading
p=Path("tmp/context398.json");saved=json.loads(p.read_text());source=saved["source"];root=saved["root"]
meta=dict(expected_version=saved["tree"]["nodes"][0]["version"],scan_container=root,scan_cell=source["outbound"],loading_context=dict(transport_task_id=source["target_trip"],scan_vehicle="QL"+source["tag"],scan_dock=source["outbound"],measurements=dict(origin="MANUAL_CONFIRMED",content_version=saved["tree"]["nodes"][0]["version"],gross_weight_kg="3",width_m="1",depth_m="1",height_m="1.5")))
op="IW399.LOAD:"+source["tag"];req=dict(contract_version=2,operation_id=op,command_type="HU_SHIP",actor="admin",source=dict(uid=root),lines=[],units=[],metadata=meta)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def native():
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   return read_oracle_json(out.getvalue())
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 if "load"not in saved:
  trial=native()
  q.execute("select count(*),sum(BASE_QTY)from RRL_IW_RECOVERY_DISPATCH where OPERATION_ID=:op",op=op);assert q.fetchone()==(1,1)
  q.execute("select count(*),sum(BASE_QTY)from RRL_INTERWARE_ONWARD_DISPATCH where OPERATION_ID=:op",op=op);assert q.fetchone()==(1,1)
  c.rollback()
  for part in saved["parts"]:
   q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot",lot=part["onward"]["pallet_identifier"]);assert q.fetchone()==(int(part['onward']['quantity']),0)
  q.execute("select count(*)from RRL_IW_RECOVERY_DISPATCH where OPERATION_ID=:op",op=op);assert q.fetchone()[0]==0;c.rollback()
  saved.update(load=build_transport_loading().load(op,root,meta,"admin"),load_operation_id=op,load_metadata=meta);p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 assert build_transport_loading().load(op,root,meta,"admin")==saved["load"]
 q.execute("select count(*)from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:op and ACTIVE_FLAG=1",op=op);assert q.fetchone()[0]==2
 for part in saved["parts"]:
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot",lot=part["onward"]["pallet_identifier"]);assert q.fetchone()==(0,0)
print("PASS393 original1+recovered1+1/3ST/oneTOP/two exactrecoverydispatch+oneoriginal/late rollback/replay/P0/no secondfulfillment")
