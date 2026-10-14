exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from copy import deepcopy
from app.modules.platform.public import read_oracle_json
from app.modules.finance.infrastructure.box_assembly_clocks import box_assembly_clocks
ctx=json.loads(Path("tmp/context519.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 q.execute("select COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=ctx["load"]);tree=read_oracle_json(q.fetchone()[0])
 original=box_assembly_clocks(q,tree,ctx["warehouse"],"UTC")
 assert len(original)==1 and original[0]["state"]=="READY",original
 for field,bad in [("instant","2020-01-01T00:00:00.000000+00:00"),("operation_id","FAKE"),("content_version",999999),("warehouse",999999)]:
  wire=deepcopy(tree);node=next(n for n in wire["nodes"]if n["uid"]==ctx["box"]);node["packing_start"][field]=bad
  assert box_assembly_clocks(q,wire,ctx["warehouse"],"UTC")[0]["state"]!="READY",field
 assert box_assembly_clocks(q,tree,ctx["warehouse"]+1,"UTC")[0]["state"]!="READY"
 q.execute("select COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT where TT_ID=33514 fetch first 1 row only")
 legacy=read_oracle_json(q.fetchone()[0]);clocks=box_assembly_clocks(q,legacy,2378876,"UTC")
 assert clocks and all(row["state"]=="ASSEMBLY_SOURCE_NOT_LINKED"for row in clocks),clocks
 case=json.loads(Path("tmp/context514.json").read_text(encoding="utf-8"))
 q.execute("select COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=case["load_operation_id"])
 case_tree=read_oracle_json(q.fetchone()[0]);assert box_assembly_clocks(q,case_tree,case["warehouse"],"UTC")[0]["state"]=="READY"
 print("PASS520 native exact BOX operation/version/instant/WARE; forged metadata and foreignWARE denied; legacy empty-creation dates not inferred; measured CASE start remains READY. Readonly.")
