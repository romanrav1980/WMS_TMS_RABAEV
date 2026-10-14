merge into RRL_SCHEMA_MIGRATIONS d
using(select '2026-10-10-165-case-current-warehouse' MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Current CASE actor/warehouse/right before replay and after native resource wait',sysdate,user,
 'db/migrations/2026-10-10_ni033_case_scope/apply.sql','db/migrations/2026-10-10_ni033_case_scope/rollback.sql',
 'APPLIED','Saved live VALID source/checkpoint; author existing replay and real mutex wait passed; no database copy/stock changes');
commit;
