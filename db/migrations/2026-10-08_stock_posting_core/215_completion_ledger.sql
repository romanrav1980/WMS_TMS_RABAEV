-- Stable ledger for installed source-checkpointed phases 208..213 and final cutover.
merge into RRL_SCHEMA_MIGRATIONS d using(
 select '2026-10-09-003-marked-stock-birth' MIGRATION_ID,'Marked inventory/production birth: exact unit capture and admission' DESCRIPTION,'208_birth_capture_apply.sql' SCRIPT_NAME,'208_birth_capture_rollback.sql' ROLLBACK_SCRIPT from dual
 union all select '2026-10-09-004-case-carrier-return','Atomic whole carrier return and cancellation; close final direct writers','210_carrier_return_apply.sql','210_carrier_return_rollback.sql' from dual
)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,s.DESCRIPTION,sysdate,user,s.SCRIPT_NAME,s.ROLLBACK_SCRIPT,'APPLIED');
commit;
/
