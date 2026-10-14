exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.public import build_stock_posting_service,StockCommand,StockPostingError
posting=build_stock_posting_service()
cancel=json.loads(Path("tmp/context307_cancel.json").read_text(encoding="utf-8"))
ctx=json.loads(Path("tmp/context307.json").read_text(encoding="utf-8"))
try:
 posting.post(StockCommand(operation_id="IW307.RECEIVE.AFTERCANCEL:"+ctx["tag"],command_type="INTERWARE_SHORTAGE_RECOVER",actor="admin",source=dict(approval_operation_id=cancel["approval_operation_id"]),lines=(),metadata={}))
except StockPostingError as exc:assert exc.oracle_code==20886 and "CANCELLED"in str(exc.rule_reason),exc
else:raise AssertionError("cancelled receipt admitted")
found=json.loads(Path("tmp/context305_recovery.json").read_text(encoding="utf-8"));part=found["parts"][0]
try:
 posting.post(StockCommand(operation_id="IW307.CANCEL.PHYSICAL:"+ctx["tag"],command_type="INTERWARE_RECOVERY_CANCEL",actor="admin",source=dict(request_operation_id=part["report_operation_id"]),lines=(),
  metadata=dict(quantity="1",reason="Попытка отмены уже фактически принятого товара",evidence_reference="DEV307:mustdenyphysical")))
except StockPostingError as exc:assert exc.oracle_code==20886 and "PHYSICALLY_RECEIVED"in str(exc.rule_reason),exc
else:raise AssertionError("physical receipt history cancelled")
print("PASS307 cancelled approval cannot receive; alreadyphysical recovery cannot cancel; no new quantity or unit effect")
