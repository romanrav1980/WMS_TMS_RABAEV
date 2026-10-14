exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_TR_VEHICLE'order by COLUMN_ID");print("VEHICLE_COLUMNS",[x[0]for x in q.fetchall()])
 for label,file in[("CTX241A:","context241a.json"),("CTX241B:","context241b.json")]:
  ctx=json.loads(Path("tmp/"+file).read_text(encoding="utf-8"));old=ctx["target_trip"];old_dock=ctx["outbound"]
  q.execute("select RRL_INTERWARE_ROUTING.target_trip(:p),RRL_INTERWARE_ROUTING.outbound_dock(:p)from dual",p=ctx["plan"]);trip,dock=q.fetchone()
  q.execute("select TRANSPORT from RRL_TRANSPORT_TASK where ID=:tt",tt=trip);plate=q.fetchone()[0]
  ctx.update(original_target_trip=old,target_trip=int(trip),original_outbound=old_dock,outbound=dock,target_vehicle_number=plate);print(label+json.dumps(ctx))
