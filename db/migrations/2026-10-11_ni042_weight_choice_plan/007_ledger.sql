merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-196-weight-choice-native-plan'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Approved whole weight box consumed by existing native planner and SOFT owner',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_choice_plan/apply.sql','db/migrations/2026-10-11_ni042_weight_choice_plan/rollback.sql','APPLIED',
'QW19612A0973586 revision277 original10/planned8/one existing source SOFT8; outer rollback/concurrent same plan/strategy conflict/cancel only after native plan cancellation/history retained/P20H0; current package VALID. Physical HARD pin197 next.');
commit;
