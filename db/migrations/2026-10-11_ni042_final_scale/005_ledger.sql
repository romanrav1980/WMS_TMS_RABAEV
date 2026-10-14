merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-204-final-scale-archive'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Whole CASE addressed empty tare and final gross in existing scale archive',sysdate,user,
'db/migrations/2026-10-11_ni042_final_scale/apply.sql','db/migrations/2026-10-11_ni042_final_scale/rollback.sql','APPLIED',
'Own QPB2044F9A6052/type10: confirmed SSCC/currentCASE6/EMPTY_TARE.100/FINAL_GROSS.400/net.300/current signature/TEST device/dedicated sender/old PICK list excludes final/append-only/no P-H/native cleanup13520/20. Original packet validator/device/archive reused; first-pick empty-tare gate. 205 same root QC mandatory once use next.');
commit;
