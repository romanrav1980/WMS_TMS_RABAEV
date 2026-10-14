exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only");r={}
 q.execute("select distinct REF_REJIM from RRL_TR_VEHICLE where REF_REJIM is not null fetch first 21 rows only");r["existing_vehicle_modes"]=[x[0]for x in q]
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where OBJECT_TYPE in('TABLE','VIEW')and(OBJECT_NAME like '%REF%'or OBJECT_NAME like '%REJ%'or OBJECT_NAME like '%REGIM%')order by OBJECT_NAME fetch first 51 rows only");r["existing_mode_objects"]=[list(x)for x in q]
 q.execute("select NAME,TYPE,LINE,TEXT from USER_SOURCE where upper(TEXT)like '%REF_REJIM%'and NAME not like 'BIN$%'order by NAME,TYPE,LINE fetch first 41 rows only");r["current_native_mode_callers"]=[list(x)for x in q]
 Path("tmp/read1139_existing_vehicle_mode.json").write_text(json.dumps(r,indent=2),encoding="utf-8");print(json.dumps(r,ensure_ascii=True))
