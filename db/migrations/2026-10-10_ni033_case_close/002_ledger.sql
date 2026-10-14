merge into RRL_SCHEMA_MIGRATIONS d
using(select '2026-10-10-167-case-carrier-close'MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'CASE close state/replay/per-line physical proof and protected command journal',sysdate,user,
 'db/migrations/2026-10-10_ni033_case_close/apply.sql','db/migrations/2026-10-10_ni033_case_close/rollback.sql',
 'APPLIED','Additive marker guard VALID; actual one-unit HTTP CASE/close rollback/replay passed in owned WARE20052672; goods and tare cleaned; original135 P20H20 unchanged');
commit;
