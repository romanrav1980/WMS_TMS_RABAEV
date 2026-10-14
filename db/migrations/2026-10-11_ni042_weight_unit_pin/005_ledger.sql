merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-197-weight-choice-physical-pin'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Exact approved physical box key for existing native HARD owners',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_unit_pin/apply.sql','db/migrations/2026-10-11_ni042_weight_unit_pin/rollback.sql','APPLIED',
'Own QW197353B7C4585 rev279 actual12 original10 CASE1073 and QW19722B684C190 rev280 actual8 original10 CASE1074; exact selected HARD physical key/storage full source20/native replenishment/actual CASE pick/replay/return/countcleanup original13520/20. Demand deviation198 next.');
commit;
