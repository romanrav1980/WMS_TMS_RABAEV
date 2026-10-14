exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.st_deferral import StDeferral
service=StDeferral(OracleGateway())
data=service.candidates("SAP_2135","admin",None,None,None,None,None,0,10,"ASSIGN")
Path("tmp/assignment1222.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
print(json.dumps({"status":"READ1222","minimum":data["minimum_date"],"rows":[r["trip_id"]for r in data["rows"]],"warehouse":data["warehouse_id"],"source_hash":data["source_hash"]}))
