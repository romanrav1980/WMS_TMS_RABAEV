merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-269-captured-day-review'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Immutable captured day review, outcome recovery and scoped history',sysdate,user,
'db/migrations/2026-10-11_ni072_review/apply.sql','db/migrations/2026-10-11_ni072_review/rollback.sql','APPLIED',
'One owned existing warehouse review/v1/native rollback/concurrent201-409/replay/body collision/currentrole/guard/sourcehash/resolve/history/P20H20. No stock/day closure or external ACK. NativeVALID/600files0cycles76/PK bounded lookup retain ownerfinance.');
commit;
