merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-198-weight-choice-demand'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original demand pending and fulfilled whole weight box adjustments',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_choice_demand/apply.sql','db/migrations/2026-10-11_ni042_weight_choice_demand/rollback.sql','APPLIED',
'Own QW19831BAC690EF rev282 original10/actual8/current waiver2 and QW19841B760AF91 rev283 original10/actual12/no negative quantity. Pending SOFT/HARD prevents duplicate original demand; exact key pick/replay/return reopens10/immutable original/native cleanup13520/20.');
commit;
