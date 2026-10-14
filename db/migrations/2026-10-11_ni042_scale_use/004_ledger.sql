merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-188-case-scale-consumption'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Once-only warehouse scale proof inside existing CASE root transaction',sysdate,user,
'db/migrations/2026-10-11_ni042_scale_use/apply.sql','db/migrations/2026-10-11_ni042_scale_use/rollback.sql','APPLIED',
'CASE1062 GROSS10.1/label NET9.8/current device/version/source/freshness/root unique lock; same saved replay/no extra stock; reuse409; native cleanup; architecture544/0/76. NET route and rollback/concurrency acceptance next.');
commit;
