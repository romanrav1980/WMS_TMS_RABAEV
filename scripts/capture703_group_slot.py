exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import hashlib
out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 for kind in("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_SLOT'and TYPE=:kind order by LINE",kind=kind)
  source="create or replace "+"".join(x[0]for x in q)+"/\n"
  out[kind]=source
raw=out["PACKAGE"]+out["PACKAGE BODY"]
Path("tmp/703_slot_before.sql").write_text(raw,encoding="utf-8")
print(json.dumps({"sha256":hashlib.sha256(raw.encode()).hexdigest(),"source_lines":len(raw.splitlines())}))
