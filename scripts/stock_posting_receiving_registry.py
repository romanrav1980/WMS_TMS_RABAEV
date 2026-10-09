"""Record the reviewed receipt/putaway writer with a frozen source digest."""
import hashlib,json
from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receiving.py")
s=p.read_text(encoding="utf-8")
for marker in ("receive_command(self.gateway","complete_existing_task(self.gateway","RECEIPT_POSTING_REQUIRED",
               "receipt_task_metadata(self.gateway"):
 if marker not in s:raise RuntimeError("Reviewed receipt writer drifted")
digest=hashlib.sha256(p.read_bytes()).hexdigest()
sql="""declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;
/
update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='"""+digest+"""',
 ADAPTER_REFERENCE='api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py;task_completion.py',
 UPDATED_AT=systimestamp
 where WRITER_KEY='LOCAL:api/wms_api_server/app/modules/inventory/infrastructure/receiving.py';
commit;
"""
print(json.dumps({"db/migrations/2026-10-08_stock_posting_core/204_receiving_writer_registry.sql":sql},ensure_ascii=True))
