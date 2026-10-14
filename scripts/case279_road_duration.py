exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.transport.public import osrm_costs,valhalla_costs,matrix_merge_statements
from app.services.routing import OsrmProvider,ValhallaProvider,HaversineProvider
from unittest.mock import patch
import httpx,uuid
data={"code":"Ok","distances":[[0,10000],[12000,0]],"durations":[[0,601],[1201,0]]}
km,minutes=osrm_costs(data,2);assert km==[[0,10],[12,0]]and minutes==[[0,10.02],[20.02,0]]
for bad in [dict(data,code="NoTable"),dict(data,durations=[[0,None],[1201,0]]),dict(data,fallback_speed_cells=[[0,1]])]:
 try:osrm_costs(bad,2)
 except ValueError:pass
 else:raise AssertionError("Unknown route became road fact")
response=httpx.Response(200,json=data,request=httpx.Request("GET","http://localhost/table"))
with patch("app.services.routing.httpx.get",return_value=response)as get:
 assert OsrmProvider().build_cost_matrix([(41,44),(42,45)])==(km,minutes)
 assert "annotations=distance,duration"in get.call_args.args[0]
val={"sources_to_targets":[[{"distance":0,"time":0},{"distance":10,"time":601}],[{"distance":12,"time":1201},{"distance":0,"time":0}]]}
assert valhalla_costs(val,2)==(km,minutes)
tag=uuid.uuid4().hex[:8];a="QA279:"+tag+":A";b="QA279:"+tag+":B"
rows,count,skip=matrix_merge_statements([{"ADDR":a},{"ADDR":b}],km,minutes,set(),"osrm");assert count==2 and skip==0
assert [x[1]["dur"]for x in rows]==[10.02,20.02]and all(x[1]["duration_basis"]=="ROAD_PROFILE_ESTIMATE"for x in rows)
fallback=matrix_merge_statements([{"ADDR":a},{"ADDR":b}],km,None,set(),"haversine")[0];assert fallback[0][1]["duration_basis"]=="SPEED_50_ESTIMATE"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 try:
  for sql,params in rows:q.execute(sql,params)
  q.execute("select DURATION_MIN,DURATION_BASIS from RRL_ADDR_DISTANCE_MATRIX where FROM_ADDR=:a and TO_ADDR=:b",a=a,b=b);assert q.fetchone()==(10.02,"ROAD_PROFILE_ESTIMATE")
 finally:c.rollback()
 q.execute("select count(*)from RRL_ADDR_DISTANCE_MATRIX where FROM_ADDR=:a",a=a);assert q.fetchone()==(0,)
 q.execute("select nullable,data_default from USER_TAB_COLUMNS where TABLE_NAME='RRL_ADDR_DISTANCE_MATRIX'and COLUMN_NAME='DURATION_BASIS'");print("SCHEMA279",q.fetchone())
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT like '%MERGE INTO RABAEV.RRL_ADDR_DISTANCE_MATRIX%'and dbms_lob.instr(SQL_FULLTEXT,'DURATION_BASIS')>0
 order by last_active_time desc fetch first 2 rows only""");print("SQL279_MS",q.fetchall())
print("LOCAL_PROVIDER_AVAILABLE",{"osrm":OsrmProvider().is_available(),"valhalla":ValhallaProvider().is_available()})
print("PASS279 provider duration seconds->ceil minutes, directional asymmetry/unknown-null-fallback rejected, exact existing matrix MERGE basis/outer rollback/no stock. Mock provider, not real road or legal admission")
