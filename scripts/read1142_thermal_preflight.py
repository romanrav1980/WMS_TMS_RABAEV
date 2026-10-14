exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.plan_preflight import TransportPreflight
from app.modules.inventory.public import read_shipping_temperature_requirements
g=OracleGateway();svc=TransportPreflight(g);r=svc.trip(33571,["SAP_2135"],"admin")
t=r["routes"][0]["temperature_requirements"]
assert len(t["items"])==2 and not t["all_ranges_configured"] and not t["vehicle_temperature_verified"],t
with g.transaction("Own1142 missing source READ ONLY")as q:
 q.execute("set transaction read only")
 empty=read_shipping_temperature_requirements(q,[],"admin");assert empty["items"]==[] and not empty["operational_admission"]
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT like 'select /* CURRENT_ST_SKU_THERMAL1142 */%'order by last_active_time desc fetch first 2 rows only")
 r["thermal_slow_sql"]=[list(x)for x in q]
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");assert q.fetchone()==(20,20)
Path("tmp/read1142_thermal_preflight.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
print(json.dumps({"case":"PASS1142","thermal":t,"slow_sql":r["thermal_slow_sql"]},ensure_ascii=True))
