exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
import httpx
ctx=json.loads(Path("tmp/context354.json").read_text(encoding="utf-8"));ware=ctx["body"]["warehouse_id"];service=LogisticsCosts(OracleGateway())
first=service.rate_history(ware,"GEL",0,1,"admin");assert first["rows"][0]["version_no"]==2 and first["next_before_version"]==2
second=service.rate_history(ware,"GEL",2,1,"admin");assert second["rows"][0]["version_no"]==1 and second["next_before_version"]is None
assert second["rows"][0]["components"]==ctx["result"]["components"]
with httpx.Client(auth=("admin","admin123"),timeout=20)as client:
 url=f"http://127.0.0.1:8088/api/finance/logistics-costs/warehouses/{ware}/rates/history"
 r=client.get(url,params=dict(currency="GEL",limit=1));assert r.status_code==200 and r.json()==first,r.text
 r=client.get(url,params=dict(currency="GEL",limit=101));assert r.status_code==422
 r=client.get(url,params=dict(currency="BADCODE",limit=1));assert r.status_code==422
Path("tmp/context355.json").write_text(json.dumps(dict(first=first,second=second),indent=2),encoding="utf-8")
print("PASS355 immutable monthly/manual history keyset pages2-to-1/currentwarehouse/typed bounds/exactcomponents/API")
