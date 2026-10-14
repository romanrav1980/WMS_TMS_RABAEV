exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import hashlib
folder=Path("db/migrations/2026-10-12_ni071_normative_correction");folder.mkdir(parents=True,exist_ok=True)
if(folder/"checkpoint.json").exists():raise SystemExit("598 sources captured already")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();sources={}
 for name in("RRL_LOG_EXPENSE_GUARD","RRL_LOG_EXP_DECISION_GUARD"):
  q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE='TRIGGER'order by LINE",name=name)
  v="create or replace "+"".join(row[0]for row in q.fetchall()).strip()+"\n/\n";assert len(v)>100,name
  sources[name]=v;(folder/("000_before_"+name.lower()+".sql")).write_text(v,encoding="utf-8")
 q.execute("select CONSTRAINT_NAME,SEARCH_CONDITION_VC from USER_CONSTRAINTS where TABLE_NAME='RRL_LOGISTICS_EXPENSE'and CONSTRAINT_TYPE='C'")
 constraints=q.fetchall()
 (folder/"checkpoint.json").write_text(json.dumps({"migration_id":"2026-10-12-598-normative-cost-correction","status":"SOURCES_ONLY_NOT_APPLIED","scope":"Extend existing expense reporting/independent LOGIST+FINANCE approval to corrections linked to original normative cost-run; no duplicate base expense or second approval subsystem.","sources_sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in sources.items()},"constraints":constraints},indent=2)+"\n",encoding="utf-8")
 print("598 actual expense/decision guard sources captured; existing approvals will be reused, no new base expense/cost counted twice; no Oracle mutation.")
