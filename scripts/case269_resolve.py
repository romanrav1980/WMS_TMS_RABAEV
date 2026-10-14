exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.finance.infrastructure.day_reviews import DayReviews
import httpx
data=json.loads(Path("tmp/context269.json").read_text(encoding="utf-8"));request=data["request"];body={k:v for k,v in request.items()if k!="operation_id"};svc=DayReviews(OracleGateway())
assert svc.resolve(request["operation_id"],body,"admin")==data["result"]
missing=svc.resolve(request["operation_id"]+".MISSING",body,"admin");assert missing["state"]=="NOT_RECORDED"
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.post("http://127.0.0.1:8088/api/finance/day-reconciliation/reviews/resolve",json=request)
 assert r.status_code==200,r.text
 assert r.json()==data["result"]
print("PASS269 resolve waits original resource plan/exact saved result/missing confirmed/native and HTTP/no new review or quantity")
