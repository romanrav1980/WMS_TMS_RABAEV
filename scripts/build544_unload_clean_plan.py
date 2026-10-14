import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni053_unloading_facts")
src=(d/"002_start_api.sql").read_text(encoding="utf-8");out={str(d/"000_before_clean_plan.sql"):src}
v=src.replace("signature varchar2(64);keys", "signature varchar2(64);savepoint_ready boolean:=false;plan_started boolean:=false;keys")
v=v.replace("  savepoint store_unload_start;\n","")
v=v.replace("RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies", "RRL_STOCK_LOCK_API.begin_plan;plan_started:=true;RRL_STOCK_LOCK_API.acquire_policies")
needle="RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);"
v=v.replace(needle,needle+"\n  savepoint store_unload_start;savepoint_ready:=true;")
v=v.replace("g_writing:=false;rollback to store_unload_start;RRL_STOCK_LOCK_API.clear_plan;raise;",
            "g_writing:=false;if savepoint_ready then rollback to store_unload_start;end if;if plan_started then RRL_STOCK_LOCK_API.clear_plan;end if;raise;")
out[str(d/"006_clean_plan.sql")]=v
out[str(d/"007_clean_plan_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-544-unload-clean-plan-before-savepoint' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Unloading metadata obeys clean-transaction stock lock acquisition before local savepoint; safe plan cleanup',sysdate,user,'006_clean_plan.sql','rollback.sql','APPLIED');
/
"""
out[str(d/"apply_clean_plan.sql")]="@@006_clean_plan.sql\n@@007_clean_plan_ledger.sql\n"
out[str(d/"apply.sql")]=(d/"apply.sql").read_text(encoding="utf-8")+"@@006_clean_plan.sql\n@@007_clean_plan_ledger.sql\n"
print(json.dumps(out))
