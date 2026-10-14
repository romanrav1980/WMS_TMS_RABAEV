exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from copy import deepcopy
from app.modules.inventory.public import normalize_unit_scan_codes
ctx=json.loads(Path("tmp/context671.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=ctx["group_store_operation_id"]);original=q.fetchone()[0]
 bad=deepcopy(original);bad["operation_id"]="STORE723.BAD:"+ctx["first"]["tag"]
 bad["metadata"]["unit_scans"]+=normalize_unit_scan_codes([dict(x,disposition="ACCEPTED")for unit in ctx["second"]["units"]for x in unit["codes"]])
 try:
  result=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(bad),"admin",result,None])
  print("PREPARED",result.getvalue()is not None)
 except oracledb.DatabaseError as e:print("REFUSAL",str(e.args[0]).split("\n")[0])
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
