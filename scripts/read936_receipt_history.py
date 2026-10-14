exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.integrations.infrastructure.supply_receipt_history import receipt_history
from app.oracle_gateway import OracleGateway
c908=json.loads(Path("tmp/context908.json").read_text(encoding="utf-8"))
c910=json.loads(Path("tmp/context910.json").read_text(encoding="utf-8"))
first=receipt_history(OracleGateway(),c908["order_id"],1,None,"admin")
assert first["consistent_snapshot"]and len(first["receipts"])==1
receipt=first["receipts"][0]
assert receipt["operation_id"]==c908["body"]["operation_id"]and receipt["accepted_quantity"]=="3"
assert receipt["current_warehouse_quantity"]=="0"and receipt["current_warehouse_hard"]=="0"
assert first["source"]["receipt_state"]=="REVERSED"and first["source"]["receipt_allowed"]is False
next_page=receipt_history(OracleGateway(),c908["order_id"],1,receipt["operation_id"],"admin")
assert next_page["receipts"]==[]and not next_page["has_more"]
try:receipt_history(OracleGateway(),c908["order_id"],1,c910["body"]["operation_id"],"admin")
except ValueError as e:assert "CURSOR_CURRENT_SOURCE"in str(e)
else:raise AssertionError("Foreign source cursor admitted")
try:receipt_history(OracleGateway(),c908["order_id"],1,None,"NONEXISTENT936")
except PermissionError:pass
else:raise AssertionError("Missing viewer admitted")
protected=json.loads(Path("tmp/context688.json").read_text(encoding="utf-8"))
live=receipt_history(OracleGateway(),protected["order_id"],50,None,"admin")
Path("tmp/history936.json").write_text(json.dumps({"own_reversed":first,"after_original":[],"foreign_cursor_refused":True,"missing_viewer_refused":True,"protected_source_read_only":live},indent=2,default=str),encoding="utf-8")
print("936 readonly PASS source908 received3/currentownP0H0/reversed; original keysetafterempty, other-source cursor denied; missingviewer denied; protected688 currenthistory read-only")
