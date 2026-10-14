exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.transport_composition import build_transport_loading
p=Path("tmp/context1194.json");d=json.loads(p.read_text(encoding="utf-8"));assert d["state"]=="READY_TO_LOAD","Continue retained only"
body=d["body"];top=d["top"];lot=d["lot"];trial=d["trial_operation"];op=d["load_operation"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot",lot=lot);assert q.fetchone()==(3,3)
 command={"contract_version":2,"operation_id":trial,"command_type":"HU_SHIP","actor":"admin","source":{"uid":top},"lines":[],"units":[],"metadata":body}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select PALLET_TYPE_ID,TYPE_ORIGIN from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=trial);assert q.fetchone()==(1,"HELD_HU_TARE_BOOK")
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=trial);assert q.fetchone()==(0,)
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot",lot=lot);assert q.fetchone()==(3,3)
 loading=build_transport_loading();result=loading.load(op,top,body,"admin");assert loading.load(op,top,body,"admin")==result
 q.execute("select PALLET_TYPE_ID,TYPE_ORIGIN,PROFILE_VERSION from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=op);assert q.fetchone()==(1,"HELD_HU_TARE_BOOK",2)
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot",lot=lot);assert q.fetchone()==(0,0)
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cl on cl.CELL=r.CELL where cl.WARE_ID=5062399");assert q.fetchone()==(20,20)
 d.update(state="LOADED",result=result,protected_stock=[20,20]);p.write_text(json.dumps(d,indent=2),encoding="utf-8")
 print(json.dumps({"case":"PASS1195","trip":d["trip_id"],"vehicle":d["vehicle_id"],"top_type":1,"top_count":1,"nodes":2,"stock":[0,0],"protected":[20,20]}))
