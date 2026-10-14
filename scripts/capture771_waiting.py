exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import hashlib
d=Path("db/migrations/2026-10-13_ni072_waiting_tasks")
files={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select USER,sys_context('USERENV','SERVICE_NAME')from dual");print("TARGET",q.fetchone(),file=sys.stderr)
 q.execute("select OBJECT_NAME from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");assert q.fetchall()==[]
 for name in ("RRL_STOCK_TASK_PLAN","RRL_STOCK_TASK_CORE","RRL_STOCK_TASK_DOMAIN","RRL_ST_DEFER_PHYSICAL"):
  for kind in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind)
   text="create or replace "+"".join(x[0]for x in q)+"/\n"
   files[str(d/("000_before_"+name.lower()+"_"+kind.lower().replace(" ","_")+".sql"))]=text
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_DEFER_WAIT_CELL_GUARD'and TYPE='TRIGGER'order by LINE")
 files[str(d/"000_before_cell_guard.sql")]="create or replace "+"".join(x[0]for x in q)+"/\n"
files[str(d/"checkpoint.json")]=json.dumps({"target":"RABAEV@127.0.0.1:1521/orcl","migration":"2026-10-13-772-st-defer-wait-task","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in files.items()}},indent=2)+"\n"
print(json.dumps(files,ensure_ascii=True))
