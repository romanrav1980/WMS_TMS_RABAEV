exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
import httpx
service=LegacyPreparation(OracleGateway())
result=service.readiness(2044,"admin")
assert result["admission_status"]=="ACCEPTED" and result["consistent_snapshot"] and not result["ready_for_operator_layout"]
line=result["lines"][0];assert line["articul"]=="QPB1991E8D6E32" and line["quantity"]=="1"
assert set(line["blockers"]) >= {"SOURCE_PICKING_CELL_MISSING","PACKAGING_MASS_DIMENSIONS_REQUIRED"}
assert not result["stock_changed"] and not result["automatic_split_verified"]
rejected=service.readiness(2045,"admin");assert "SOURCE_NOT_ADMITTED" in rejected["blockers"]
try:service.readiness(2044,"SAP_FILE_GATEWAY")
except PermissionError:pass
else:raise AssertionError("Gateway read permission bypass")
with httpx.Client(auth=("admin","admin123"),timeout=30) as client:
 response=client.get("http://127.0.0.1:8088/api/integrations/sap/store-orders/2044/preparation-readiness")
 assert response.status_code==200,response.text
 assert response.json()==result
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 q.execute("select count(*)from RRL_SBORKA_PALLETS where ST_NUMBER='SAP_2044'");assert q.fetchone()==(0,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like '%SOURCE_PICKING_READINESS268%'and executions>0")
 print("SQL_MS",q.fetchall())
print("PASS268 accepted source reports missing actual logistics/rejected denied/current service permission denied/HTTP same snapshot/no legacy ST or stock birth")
