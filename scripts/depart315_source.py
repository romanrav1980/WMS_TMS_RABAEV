exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.transport_composition import build_transport_loading
p=Path("tmp/context315.json");ctx=json.loads(p.read_text(encoding="utf-8"))
if "departure_result"not in ctx:
 ctx["departure_result"]=build_transport_loading().depart("IW315.DEPART:"+ctx["source"]["tag"],ctx["source"]["target_trip"],"admin")
 p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("SOURCE315 actual nested3 departed for nextwarehouse; originalSKU/units/codes unchanged, no STOREreceipt")
