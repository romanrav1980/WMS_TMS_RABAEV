exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.public import normalize_unit_scan_codes,normalize_interwarehouse_scans
from copy import deepcopy
ctx=json.loads(Path("tmp/context671.json").read_text(encoding="utf-8"))
proof=ctx["group_store_preview"]["marked_unit_control"];assert proof["supported"]and proof["physical_unit_count"]==6
source=ctx["group_store_metadata"]
metadata={"unit_scans":normalize_unit_scan_codes(source["scans"]),"aggregation_scans":[dict(normalize_interwarehouse_scans({"aggregation_scans":[{k:v for k,v in x.items()if k!="disposition"}]})["aggregation_scans"][0],disposition=x["disposition"])for x in source["aggregation_scans"]]}
lines=[dict(lot_uid=x["lot"],accepted="3",missing="0",refused="0",damaged="0",extra="0")for x in(ctx["first"],ctx["second"])]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def resolve(value):
  result=q.var(oracledb.DB_TYPE_CLOB)
  q.execute("""declare p json_object_t:=json_object_t.parse(:proof);m json_object_t:=json_object_t.parse(:metadata);l json_array_t:=json_array_t.parse(:lines);u json_array_t;begin RRL_STORE_MARK_CORE.resolve_disposition(p,m,l,u);:result:=u.to_clob;end;""",proof=json.dumps(proof),metadata=json.dumps(value),lines=json.dumps(lines),result=result)
  from app.modules.platform.public import read_oracle_json
  return read_oracle_json(result.getvalue())
 assert len(resolve(metadata))==6
 bad=[]
 v=deepcopy(metadata);v["unit_scans"]+=normalize_unit_scan_codes([dict(x,disposition="ACCEPTED")for unit in ctx["second"]["units"]for x in unit["codes"]]);bad.append(("direct_fallback",v))
 v=deepcopy(metadata);v["aggregation_scans"][0]["code_hash"]="0"*64;bad.append(("foreign",v))
 v=deepcopy(metadata);v["aggregation_scans"].append(v["aggregation_scans"][0]);bad.append(("duplicate",v))
 v=deepcopy(metadata);v["aggregation_scans"][0]["disposition"]="DAMAGED";bad.append(("inconsistent_decisions",v))
 for name,value in bad:
  try:resolve(value)
  except oracledb.DatabaseError as e:assert 20800<=e.args[0].code<=20999,(name,str(e))
  else:raise AssertionError("Accepted "+name)
 c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1)from V$SQL where sql_text like '%STORE_AGGREGATION_ONLY%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL",q.fetchall())
print("PASS719 actual frozen six-key proof/shared aggregate resolver; direct fallback/foreign/duplicate/inconsistent disposition rejected; no DML/P20H20 unchanged")
