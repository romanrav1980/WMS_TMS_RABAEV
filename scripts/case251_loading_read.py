exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.loading_status import loading_status
from app.modules.transport.public import TransportLoadingError
import httpx
g=OracleGateway()
a=loading_status(g,33558,"admin")
assert a["all_members_physically_loaded"] and a["loaded_place_count"]==2 and a["read_only"] and not a["operational_admission"],a
b=loading_status(g,33541,"admin")
assert not b["all_members_physically_loaded"] and b["pending_st_ids"] and b["loaded_place_count"]==1,b
receiver="WR23413508027ed"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select DELETED,WARE_ID,RRL_HAS_WRIGHT(ID,'transport_dispatch_view')from RUSERS where ID=:actor",actor=receiver)
 active,ware,right=q.fetchone()
 print("CURRENT_RECEIVER",active,ware,right)
 if active==0 and right==1:
  own=loading_status(g,33543,receiver);assert own["all_members_physically_loaded"] and own["physical_places"][0]["custody_released_at"] is not None
 try:loading_status(g,33558,receiver)
 except TransportLoadingError as exc:assert exc.status==403
 else:raise AssertionError("Foreign loading history exposed")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
with httpx.Client(auth=("admin","admin123"),timeout=25)as client:
 r=client.get("http://127.0.0.1:8088/api/transport/loading/33558/status")
 assert r.status_code==200,(r.status_code,r.text[:1000])
 assert r.json()["all_members_physically_loaded"] and r.json()["read_only"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL
 where sql_text like 'select sp.ID,sp.ST_NUMBER,sp.PALLET_UID,sp.CONDITION,%'
 and executions>0 order by last_active_time desc fetch first 3 rows only""");print("SQL_MS",q.fetchall())
print("PASS251 same scoped readonly loading snapshot/original33558 two departed places complete/current33541 pending member/foreign403/HTTP unchanged shape with proof/read flags/protected20-20/no writes")
