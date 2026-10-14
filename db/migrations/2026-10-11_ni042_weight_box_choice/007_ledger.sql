merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-195-approved-weight-box-choice'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Immutable approval-only final whole box choice inside existing business metadata owner',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_choice/apply.sql','db/migrations/2026-10-11_ni042_weight_box_choice/rollback.sql','APPLIED',
'Own QW1952E694BA0DE actual8/12 vs original10/default15/no split; approval-only actor/source signature/rawGS1/replay/conflicts/active unique/cancel history/current active status/P20H0 unchanged; no plan or stock effect; existing native planner use next.');
commit;
