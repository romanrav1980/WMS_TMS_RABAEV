merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-194-weight-box-planning-read'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Actual whole weighted box options and shared current warehouse planner admission',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_planning/apply.sql','db/migrations/2026-10-11_ni042_weight_box_planning/rollback.sql','APPLIED',
'Own SKU QW19416DCF25046 original10, actual source boxes8/12/gross8.3/12.3/volume.024/.036/current signed source/default15/both explicit exceptions/no split/P20H0 unchanged; foreign warehouse refused; no saved choice yet.');
commit;
