merge into RRL_SCHEMA_MIGRATIONS d
using(select '2026-10-11-174-remaining-pick-plan' MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing planner consumes current native remaining demand and unlaunched SOFT under sorted scoped locks',sysdate,user,
'db/migrations/2026-10-11_ni032_remaining_plan/apply.sql','db/migrations/2026-10-11_ni032_remaining_plan/rollback.sql','APPLIED',
'Owned original1931 row3416 requested4 shipped3: concurrent one plan1911 requested/planned1 SOFT1, other20886/no partial DRAFT; native plan cancel/count cleanup; original135 P20H20');
commit;
