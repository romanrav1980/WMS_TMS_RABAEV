exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
folder=Path("db/migrations/2026-10-12_ni061_nested_receiving");out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TRIGGER_NAME,TRIGGERING_EVENT from USER_TRIGGERS where TABLE_NAME in('RRL_PALLETS','RRL_WMS_HU_LINK')");print("Triggers",q.fetchall(),file=sys.stderr)
 names=["RRL_STOCK_INTERWARE_REC","RRL_INTERWARE_PLAN_GUARD","RRL_HU_CONTAINER_GUARD","RRL_HU_LINK_WRITE_GUARD","RRL_HU_DEPARTURE_GUARD","RRL_HU_TARE_WARE_GUARD","RRL_SAP_PALLET_WRITE_GUARD"]
 for name in names:
  kind="PACKAGE BODY"if name=="RRL_STOCK_INTERWARE_REC"else"TRIGGER"
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=name,kind=kind);body="".join(r[0]for r in q).replace(chr(13)," ").strip()
  if body:out[(folder/("000_before_"+name.lower()+".sql")).as_posix()]="create or replace "+body+"\n/\n"
print(json.dumps(out))
