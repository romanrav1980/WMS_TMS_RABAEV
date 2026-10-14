exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
source=json.loads(Path("tmp/context328.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:q.execute("update RRL_TR_VEHICLE set PALLETS=2 where NUM=:plate",plate="QL"+source["tag"]);assert q.rowcount==1;c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
print("Own330 fixture vehicle declares2 plannedplaces; actualtopplace1 will be verified separately")
