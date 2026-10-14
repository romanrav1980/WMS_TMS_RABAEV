merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-189-case-scale-net'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Current unmarked KG NET scale route and original capture source validation',sysdate,user,
'db/migrations/2026-10-11_ni042_scale_net/apply.sql','db/migrations/2026-10-11_ni042_scale_net/rollback.sql','APPLIED',
'CASE1063 NET9.6/P20H10/PARTIAL remaining.4; CASE1064 outer rollback all/root concurrent two IDs one winner1064:B/loser409/saved replay/native cleanup. Quality544/0/76/24/bothTS PASS; device hardware/order tolerance separate.');
commit;
