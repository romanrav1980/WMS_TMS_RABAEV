exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_PICK_WAVE_API'and TYPE='PACKAGE BODY'order by LINE")
 src="".join(row[0]for row in q)
 for start,end in [("  function create_wave(","  end create_wave;"),("  procedure add_plan(","  end add_plan;")]:
  a=src.lower().find(start);b=src.lower().find(end,a);print(src[a:b+len(end)])
 q.execute("select PICK_WAVE_ID,WAVE_CODE,STATUS,WARE_ID from RRL_PICK_WAVE where WARE_ID=9807 order by PICK_WAVE_ID desc fetch first 6 rows only")
 print(json.dumps({"waves":q.fetchall()}))
