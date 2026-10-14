exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
files={};root="db/migrations/2026-10-14_ni022_prepared_row_move/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 for name,typ in [("RRL_STOCK_POSTING_API","PACKAGE BODY"),("RRL_UPDATE_SBORKA_PALLET_ROWS2","FUNCTION")]:
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=typ)
  body="".join(x[0]for x in q).replace("\r","")
  assert body.strip();files[root+"000_"+name.lower()+".sql"]="create or replace "+body.rstrip()+"\n/\n"
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%' order by OBJECT_NAME")
 files[root+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-14-1265-prepared-row-move","target":"RABAEV/orcl","invalid_before":q.fetchall(),"state":"PREPARED"},indent=2)
print(json.dumps(files))
