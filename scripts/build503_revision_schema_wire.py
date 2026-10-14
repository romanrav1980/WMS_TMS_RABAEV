import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni071_rate_revision")
out={str(d/"apply.sql"):"@@003_versioned_period.sql\n@@001_guard.sql\n@@002_ledger.sql\n",
str(d/"rollback.sql"):"declare n number;begin select count(*)into n from(select RATE_KEY,EFFECTIVE_FROM from RRL_LOGISTICS_RATE_HISTORY group by RATE_KEY,EFFECTIVE_FROM having count(*)>1);if n>0 then raise_application_error(-20899,'SAME_PERIOD_REVISION_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;\n/\n@@000_before_guard.sql\n-- Restore previous Python selector/operator and date uniqueness together only before any revised period is committed.\n"}
print(json.dumps(out))
