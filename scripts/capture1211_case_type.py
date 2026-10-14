import json
from pathlib import Path
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
names=["RRL_STOCK_WRITE_GUARD","RRL_STOCK_CASE_PICK_CMD","RRL_CASE_TASK_ACCESS","RRL_CASE_RESOURCE_POLICY"]
files={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=5000;q=c.cursor()
 for name in names:
  q.execute("select TYPE,TEXT from USER_SOURCE where NAME=:name order by TYPE,LINE",name=name)
  groups={}
  for typ,text in q:groups.setdefault(typ,[]).append(text)
  for typ,text in groups.items():files["tmp/1211_"+name.lower()+"_"+typ.lower().replace(" ","_")+".sql"]="create or replace "+"".join(text)+"\n/\n"
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_CASE_PICK_TASK'")
 for name, in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE='TRIGGER' order by LINE",name=name)
  files["tmp/1211_"+name.lower()+".sql"]="".join(r[0]for r in q)
print(json.dumps(files,ensure_ascii=True))
