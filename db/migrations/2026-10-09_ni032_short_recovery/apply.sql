prompt NI03.2 linked shortage inventory and recovery; checkpoints 225-233
@@001_schema.sql
@@004_transit_fences.sql
@@../2026-10-08_stock_posting_core/142_metadata_fence.sql
@@002_contract.sql
@@../2026-10-08_stock_posting_core/020_reservations.sql
@@../2026-10-08_stock_posting_core/039_unit_core.sql
@@003_recovery.sql
@@../2026-10-09_ni031_stock_eligibility/002_policy.sql
@@../2026-10-08_stock_posting_core/102_inventory_count.sql
@@../2026-10-08_stock_posting_core/171_case_short_command.sql
@@007_task_plan.sql
@@006_task_core.sql
@@../2026-10-08_stock_posting_core/035_task_domain.sql
@@009_wave.sql
@@008_case.sql
@@../2026-10-08_stock_posting_core/209_case_return.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-010-short-recovery' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI03.2 linked shortage inventory/urgent replenishment/direct confirmed stock recovery',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
