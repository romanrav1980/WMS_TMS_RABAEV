merge into RRL_SCHEMA_MIGRATIONS d
using(select '2026-10-11-172-mixed-wave-decision'MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Mixed shipped/cancelled wave decision preserving native shipped facts and current source demand',sysdate,user,
 'db/migrations/2026-10-11_ni033_mixed_wave/apply.sql','db/migrations/2026-10-11_ni033_mixed_wave/rollback.sql',
 'APPLIED','Actual owned403 task839 full3/independent synthetic item-scan and weight QC/shipment; CASE1038 empty1 cancelled; native rollback+concurrent mixed finish; original line remaining0/1 and P20H20 retained');
commit;
