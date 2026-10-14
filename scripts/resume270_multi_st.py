exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.plan_application import assign_validated_sts
import httpx
data=json.loads(Path("tmp/context270.json").read_text(encoding="utf-8"));number=data["number"];trip=data["trip"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,TRANSTASK_ID from RRL_SBORKA_PALLETS where ST_NUMBER=:st_number order by ID",st_number=number)
 rows=q.fetchall();assert [int(r[0])for r in rows]==data["ids"] and all(r[1]in(None,0)for r in rows),rows
result=assign_validated_sts(OracleGateway(),trip,[number],"admin");assert result["written_sts"]==1
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 response=client.post(f"http://127.0.0.1:8088/api/admin/transport/tasks/{trip}/sts",json={"st_numbers":[number]})
 assert response.status_code==200,response.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_SBORKA_PALLETS where ST_NUMBER=:st_number and TRANSTASK_ID=:trip_id",st_number=number,trip_id=trip);assert q.fetchone()==(2,)
 q.execute("select sum(QUANTITY),sum(ORDER_WEIGHT),sum(PACK_COUNT)from RRL_SBORKA_PALLET_ROWS where DOCID=:st_number",st_number=number);assert q.fetchone()==(48,20,2)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where SQL_TEXT like '%COUNT(CASE WHEN CONDITION=2%'and executions>0");print("SQL_MS",q.fetchall())
print("PASS270 recovered same owned2pallets/native rollback confirmed before current bind fix/actual native assign+HTTPrepeat/48planned20kg2packs preserved/P20H20/no stock or newtrip/old time route source now stale requires review")
