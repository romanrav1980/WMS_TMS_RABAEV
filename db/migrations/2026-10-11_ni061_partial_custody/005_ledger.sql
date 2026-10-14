merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-296-partial-custody-onward'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing first-leg custody and actual accepted fragment onward after confirmed shortage',sysdate,user,'db/migrations/2026-10-11_ni061_partial_custody/001_custody_body.sql','db/migrations/2026-10-11_ni061_partial_custody/rollback.sql','APPLIED','Ordinary and marked accepted1+confirmedshort2, actual custody rollback/race/replay/ST1/assigned/QC/load/depart, fullreceiptfalse. Source archive andsixcodes retained/protected20-20. Finalrecipient/recovery/independent pending.');
commit;
