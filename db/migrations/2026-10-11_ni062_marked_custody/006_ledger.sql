merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-233-original-marked-store-return-custody'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original marked return handover and dedicated driver scan exact approved units',sysdate,user,'db/migrations/2026-10-11_ni062_marked_custody/apply.sql','db/migrations/2026-10-11_ni062_marked_custody/rollback.sql','APPLIED','Actual one approved unit/two profiles RET233.HAND:13508027ed1 and RET233.PICKUP:13508027ed; rollback/concurrent/replay/current binding403/no quantity/protected20-20. Assumed XML via existing gateway; no external ACK.');
commit;
