merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-210-case-stacking-stage'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Versioned WMS SKU stacking stage frozen on issued CASE line',sysdate,user,
'db/migrations/2026-10-11_ni042_stack_stage/apply.sql','db/migrations/2026-10-11_ni042_stack_stage/rollback.sql','APPLIED',
'Own CASE1107/wave461/BASE then TOP/native picks1+1, issued policy1 stays after future swapped SKU stage, omission preserves new stage, immutable direct update20863. CASE1108/wave462 TOP then BASE409 before first movement. Both native cleanup0/protected13520/20; six invalidated dependencies explicitly compiled.');
commit;
