prompt NI03.2 physical PUTAWAY capability and open-shift execution
@@001_capability.sql
@@002_warehouse_policy.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-017-putaway-capability' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'PUTAWAY supported by existing forklift/reachtruck types with individual qualification; physical execution only in open shift',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
