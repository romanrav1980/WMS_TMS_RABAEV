merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-193-weight-deviation-demand'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Current cancellation-aware accepted weight deviation in original pool demand math',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_demand/apply.sql','db/migrations/2026-10-11_ni042_weight_demand/rollback.sql','APPLIED',
'CASE1071 short21 original10/actual9.6/H9.6/accepted.4/current demand0; native CASE return demand10/waiver0, immutable approval retained. No stock writes/new allocator. Quality545/0/76/24/bothTS PASS.');
commit;
