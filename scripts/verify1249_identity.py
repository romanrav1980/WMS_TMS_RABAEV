exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select LINE,POSITION,TEXT from USER_ERRORS where NAME='RRL_PICKING_API'")
 errors=q.fetchall();print(json.dumps({"errors":errors}));assert not errors
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'")
 now=set(map(tuple,q.fetchall()));before=set(map(tuple,json.loads(Path("db/migrations/2026-10-14_ni033_pick_article_identity/000_invalid_before.json").read_text())))
 print(json.dumps({"new_invalid":sorted(now-before)}));assert not now-before
