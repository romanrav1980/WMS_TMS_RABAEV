exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
data=json.loads(Path("tmp/context248.json").read_text(encoding="utf-8"));trip=data["trip_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:
  q.execute("select USER_ID,CONDITION from RRL_TRANSPORT_TASK where ID=:trip_id for update",trip_id=trip)
  owner,state=q.fetchone();assert owner=="admin" and state=="?"*11,(owner,state)
  q.execute("select count(*)from RRL_SBORKA_PALLETS where TRANSTASK_ID=:trip_id",trip_id=trip);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_TT_TIME_APPROVAL where TT_ID=:trip_id",trip_id=trip);assert q.fetchone()[0]==0
  q.execute("update RRL_TRANSPORT_TASK set CONDITION=:state where ID=:trip_id",state="Спланирован",trip_id=trip)
  q.callproc("RRL_STOCK_METADATA_TX.end_change");c.commit()
 except:
  c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change");raise
print("Own248 original newly created empty fixture status corrected; no old population change")
