merge into RRL_SCHEMA_MIGRATIONS d
using(select '2026-10-10-169-wave-deferred-demand'MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Explicit returned wave decision/current actor warehouse/native replay and source closure',sysdate,user,
 'db/migrations/2026-10-10_ni033_wave_defer/apply.sql','db/migrations/2026-10-10_ni033_wave_defer/rollback.sql',
 'APPLIED','Packages VALID; native rollback401, fresh concurrent401 one decision, saved402 scope/replay; original order demand1 and P20H20 unchanged');
commit;
