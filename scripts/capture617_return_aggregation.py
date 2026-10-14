exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
folder=Path("db/migrations/2026-10-12_ni062_return_aggregation");folder.mkdir(parents=True,exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in("RRL_STORE_RETURN_UNIT_CORE","RRL_IW_AGG_SCAN"):
  for kind in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE",name=name,kind=kind)
   source="create or replace "+"".join(row[0]for row in q.fetchall()).strip()+"\n/\n";assert len(source)>100,name
   path=folder/("000_before_"+name.lower()+"_"+kind.lower().replace(" ","_")+".sql")
   if path.exists():assert path.read_text(encoding="utf-8").replace("\r","")==source.replace("\r",""),"Do not overwrite drifted checkpoint"
   else:path.write_text(source,encoding="utf-8")
 print("617 original return-unit and shared aggregation resolver sources captured read-only, no new goods engine.")
