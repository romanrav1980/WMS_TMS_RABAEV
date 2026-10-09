"""Record reviewed MES service routes; physical effects remain in the Oracle core."""
import hashlib,json
from pathlib import Path
p=Path("api/wms_api_server/app/services/mes_service.py")
s=p.read_text(encoding="utf-8")
for marker in ("post_existing_mes_task(self.gateway","calculate_existing_mes_supply(self.gateway",
 "release_supply(self.gateway","apply_mes_movements(self.gateway","MES_RESERVATION_POSTING_REQUIRED",
 "quantity=Decimal(str(fact_qty))","pallet.model_dump(mode='json')"):
 if marker not in s:raise RuntimeError("Reviewed MES writer drifted: "+marker)
digest=hashlib.sha256(p.read_bytes()).hexdigest()
sql="""declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;
/
update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='"""+digest+"""',
 ADAPTER_REFERENCE='api/wms_api_server/app/modules/inventory/infrastructure/mes_commands.py;mes_task_commands.py;mes_supply_commands.py',
 UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:api/wms_api_server/app/services/mes_service.py';
commit;
"""
report=json.loads(Path("runtime/stock_posting_20261008/checkpoint/writer-checkpoint.json").read_text(encoding="utf-8"))
old=next(r["sha256"] for r in report["local_writers"] if r["path"]==str(p).replace("\\","/"))
rollback="""declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;
/
update RRL_STOCK_WRITER_REGISTRY set STATE='UNCONVERTED',SOURCE_HASH='"""+old+"""',
 ADAPTER_REFERENCE=null,UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:api/wms_api_server/app/services/mes_service.py';
commit;
"""
d=Path("db/migrations/2026-10-08_stock_posting_core")
print(json.dumps({str(d/"205_mes_writer_registry.sql"):sql,str(d/"205_mes_writer_registry_rollback.sql"):rollback},ensure_ascii=True))
