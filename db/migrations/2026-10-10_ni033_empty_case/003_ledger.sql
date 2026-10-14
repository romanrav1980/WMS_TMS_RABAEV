merge into RRL_SCHEMA_MIGRATIONS d
using(select '2026-10-10-170-case-empty-cancel'MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing CASE return supports explicit empty cancellation; held tare blocks wave closure',sysdate,user,
 'db/migrations/2026-10-10_ni033_empty_case/apply.sql','db/migrations/2026-10-10_ni033_empty_case/rollback.sql',
 'APPLIED','Native CASE1033/H1 rollback and concurrent cancellation; CASE1034 tare held refusal/release and wave399 completion; own goods/tare zero, original P20H20 unchanged');
commit;
