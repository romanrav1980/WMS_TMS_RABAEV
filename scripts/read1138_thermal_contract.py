exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only");r={}
 for table in("RRL_RECEIPT_SKU_RULE","RRL_RECEIPT_CELL_RULE","RRL_TR_VEHICLE"):
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:t order by COLUMN_ID",t=table);r[table]=[list(x)for x in q]
 q.execute("select OBJECT_NAME,PROCEDURE_NAME from USER_PROCEDURES where OBJECT_NAME like '%THERM%'order by OBJECT_NAME,PROCEDURE_NAME");r["thermal_native_methods"]=[list(x)for x in q]
 Path("tmp/read1138_thermal_contract.json").write_text(json.dumps(r,indent=2),encoding="utf-8");print(json.dumps(r,ensure_ascii=True))
