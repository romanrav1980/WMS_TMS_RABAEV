merge into RRL_SCHEMA_MIGRATIONS d
using(select '2026-10-11-171-existing-line-demand'MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Targeted original line demand reuses existing pool arithmetic without stock mutation',sysdate,user,
 'db/migrations/2026-10-11_ni033_line_demand/apply.sql','db/migrations/2026-10-11_ni033_line_demand/rollback.sql',
 'APPLIED','Pool and dependent command VALID; exact original snapshot/shape/order for existing two warehouses/eight rows unchanged; line helper same values');
commit;
