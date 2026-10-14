exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.receiving import Receiving
from app.modules.inventory.api.receiving_routes import PalletReceipt
from app.oracle_gateway import OracleGateway
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"))
body={"operation_id":"f299b94a-03fe-4ed1-a499-db937e0f40d6","line_number":"1","sscc":"B01.1238:c0c2a00c0b:1","quantity":"18","product_barcode":"QA1118c0c2a00c0b0","supplier_batch":"B01.1238:c0c2a00c0b","expiry_date":"2030-01-01","produced_date":None,"gross_weight":"12","pallet_height":"1","pallet_height_m":"1","volume_m3":"0.05","units":[],"aggregations":[]}
ctx["pending_receipt_body"]=body;Path("tmp/context1238.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
result=Receiving(OracleGateway()).receive(ctx["supply"]["order_id"],PalletReceipt.model_validate(body).model_dump(mode="json"),"admin")
ctx["first_receipt"]=result;ctx["stage"]="FIRST_RECEIVED";Path("tmp/context1238.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print(json.dumps(result,default=str))
