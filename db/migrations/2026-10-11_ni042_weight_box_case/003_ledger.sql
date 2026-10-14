merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-182-weighted-case-label'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Weighted box scan adapts to existing CASE_PICK_CONFIRM, server cumulative KG, native label/unit/own HARD validation',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_case/apply.sql','db/migrations/2026-10-11_ni042_weight_box_case/rollback.sql','APPLIED',
'Actual wave415 CASE1055 CASE.WEIGHT182:1055 picked9.8KG/unit1/exact replay/changed label409; source total19.6 H9.8; native return/count cleanup/waveDONE/original135 P20H20; TSD durable weighted intent; bounded fixture no volume cap; variable-box capacity remains separate');
commit;
