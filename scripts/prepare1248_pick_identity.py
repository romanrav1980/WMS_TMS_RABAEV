exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
folder=Path("db/migrations/2026-10-14_ni033_pick_article_identity");folder.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select sys_context('USERENV','CURRENT_SCHEMA'),sys_context('USERENV','SERVICE_NAME')from dual");print(q.fetchone())
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_PICKING_API'and TYPE='PACKAGE BODY'order by LINE")
 before="create or replace "+"".join(x[0]for x in q).replace("\r","")+"\n/\n"
 assert not (folder/"000_before.sql").exists(),"Checkpoint already exists"
 (folder/"000_before.sql").write_text(before,encoding="utf-8")
 after=before
 assert after.count("upper(substr(l.ARTICUL, 1, 40))")==4
 after=after.replace("upper(substr(l.ARTICUL, 1, 40))","case when v_release='ACTIVE' then l.ARTICUL else upper(substr(l.ARTICUL, 1, 40)) end")
 old="and upper(p.ARTICUL) = upper(l.ARTICUL)"
 assert after.count(old)==1
 after=after.replace(old,"and ((v_release='ACTIVE' and p.ARTICUL=l.ARTICUL) or (v_release!='ACTIVE' and upper(p.ARTICUL)=upper(l.ARTICUL)))")
 (folder/"001_picking.sql").write_text(after,encoding="utf-8")
 q.execute("select PICK_RESERVATION_ID,ARTICUL,RESERVED_QTY,RESERVATION_LEVEL from RRL_PICK_RESERVATION where PICK_PLAN_ID=2190")
 print(json.dumps({"before_reservations":q.fetchall()}))
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'")
 (folder/"000_invalid_before.json").write_text(json.dumps(q.fetchall()),encoding="utf-8")
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_PICK_WAVE_API'and TYPE='PACKAGE BODY'order by LINE")
 wave="".join(x[0]for x in q);Path("tmp/wave1248.sql").write_text(wave,encoding="utf-8")
print(str(folder))
