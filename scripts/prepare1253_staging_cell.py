exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"));assert ctx["stage"]=="WAVE_LAUNCHED"
cell="B38"+ctx["tag"][:8]+"E"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*) from RRL_CELLS where CELL=:cell",cell=cell)
 if not q.fetchone()[0]:
  q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,EXPEDITION_GROUP)values(:cell,9807,4,1,1,0,1,1000,3,'B01.DEV')",cell=cell)
  q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
 c.commit()
ctx["staging_cell"]=cell;Path("tmp/context1238.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print(json.dumps({"staging_cell":cell,"stock_changed":False}))
