exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.modules.finance.contracts import LogisticsCostError
from app.oracle_gateway import OracleGateway
import httpx
source=json.loads(Path("tmp/context348.json").read_text(encoding="utf-8"))["sources"][0]
p=Path("tmp/context354.json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else{}
body=dict(warehouse_id=source["target_warehouse"],currency="GEL",month="2026-11",picking_rate="2",common_work_amount="800",basis_boxes="1600",expected_version=0,reason="Own354 monthly normative shared work included once",decision_reference="DEV354:"+source["tag"])
client=httpx.Client(auth=("admin","admin123"),timeout=35);url="http://127.0.0.1:8088/api/finance/logistics-costs/rates/monthly"
r=client.post(url,json=body);assert r.status_code==200,r.text;result=r.json()
assert result["rate"]=="2.5"and result["components"]["common_work_rate"]=="0.5"and result["common_work_included"]is True,result
assert client.post(url,json=body).json()==result
r=client.post(url,json={**body,"common_work_amount":"400","basis_boxes":"800"});assert r.status_code==409,r.text
r=client.post(url,json={**body,"month":"2026-13"});assert r.status_code==422,r.text
r=client.post(url,json={**body,"basis_boxes":"0"});assert r.status_code==422,r.text
service=LogisticsCosts(OracleGateway())
if "future"not in saved:saved["future"]=service.rate(body["warehouse_id"],"GEL","9","2027-01-01",1,"Own354 future manual norm","DEV354:FUTURE","admin");p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
assert client.post(url,json=body).json()==result
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*),max(VERSION_NO)from RRL_LOGISTICS_RATE_HISTORY where RATE_KEY=:key",key=result["rate_key"]);assert q.fetchone()==(2,2)
 q.execute("select count(*)from RRL_LOGISTICS_COST_RUN where WARE_ID=:ware",ware=body["warehouse_id"]);assert q.fetchone()[0]==0
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
saved.update(body=body,result=result,current_rates=service.rates(body["warehouse_id"],"admin"));p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
print("PASS354 monthly shared800/1600=.5 +base2=2.5 inoriginalrate; immutable components/replay afterfuturev2/same-total changedbase409/badmonth-zero422/no charge/protected20-20")
