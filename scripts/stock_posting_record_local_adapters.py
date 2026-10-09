"""Record only reviewed service entrypoints that cannot conduct legacy stock after ACTIVE."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS = {
 "api/wms_api_server/app/modules/inventory/infrastructure/task_stock_move.py": (
    "apply_task_stock_move", "Use TASK_COMPLETE before synchronizing physical stock",
    "api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py"),
 "api/wms_api_server/app/modules/inventory/infrastructure/task_reservation.py": (
    "apply_replenishment_reservation", "Use TASK_COMPLETE before synchronizing reservation coverage",
    "api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py"),
 "api/wms_api_server/app/services/warehouse_task_domain_sync_service.py": (
    "_explicit_sync", "TASK_POSTING_REQUIRED",
    "api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py"),
 "api/wms_api_server/app/services/stock_reservation_service.py": (
    "post_reservation", "RESERVATION_",
    "api/wms_api_server/app/modules/inventory/infrastructure/reservation_commands.py"),
}
statements=["declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;"
 "if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;\n/\n"]
for path,(entry,marker,reference) in ITEMS.items():
    content=(ROOT/path).read_text(encoding="utf-8")
    referenced=(ROOT/reference).read_text(encoding="utf-8")
    if entry not in content or marker not in content+referenced:
        raise RuntimeError("Reviewed adapter has changed: "+path)
    digest=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    statements.append("update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='"+digest+
        "',ADAPTER_REFERENCE='"+reference+"',UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:"+path+"';")
statements.append("commit;\n")
print(json.dumps({"144_local_writer_registry.sql":"\n".join(statements)},ensure_ascii=True))
