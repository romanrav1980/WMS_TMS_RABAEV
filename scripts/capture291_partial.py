exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};base="db/migrations/2026-10-11_ni061_partial_receiving/"
names=["RRL_STOCK_INTERWARE_REC","RRL_STOCK_INTERWARE_PUT","RRL_INTERWARE_UNIT_SOURCE","RRL_STOCK_INTERWARE_CUSTODY","RRL_STOCK_UNIT_CORE","RRL_STOCK_POSTING_API"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in names:
  for kind in ["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:object_name and TYPE=:object_type order by LINE",object_name=name,object_type=kind)
   text="".join(r[0]for r in q)
   assert text
   out[base+"000_before_"+name.lower()+("_spec"if kind=="PACKAGE"else"_body")+".sql"]="create or replace "+text+"\n/\n"
 for table in ["RRL_INTERWARE_PLAN","RRL_INTERWARE_RECEIPT"]:
  q.execute("select dbms_metadata.get_ddl('TABLE',:object_name,user)from dual",object_name=table)
  out[base+"000_before_"+table.lower()+".sql"]=q.fetchone()[0].read()+"\n"
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME in('RRL_WMS_RECEIPT_UNIT','RRL_PALLETS','RRL_INTERWARE_RECEIPT')")
 triggers=[r[0]for r in q];print("TRIGGERS291",triggers,file=sys.stderr)
 for name in triggers:
  q.execute("select dbms_metadata.get_ddl('TRIGGER',:object_name,user)from dual",object_name=name)
  out[base+"000_before_"+name.lower()+".sql"]=q.fetchone()[0].read()+"\n"
 q.execute("select p.OPERATION_ID,p.ROOT_UID,p.TARGET_WARE_ID from RRL_INTERWARE_PLAN p where not exists(select 1 from RRL_INTERWARE_RECEIPT r where r.PLAN_OPERATION_ID=p.OPERATION_ID)order by p.CREATED_AT fetch first 5 rows only")
 print("UNRECEIVED291",q.fetchall(),file=sys.stderr)
print(json.dumps(out,ensure_ascii=True))
