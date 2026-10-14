merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-250-approved-transport-resource-overlap'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original ARM time publication refuses current approved driver or vehicle overlap',sysdate,user,
'db/migrations/2026-10-11_ni081_time_resource_gate/apply.sql','db/migrations/2026-10-11_ni081_time_resource_gate/rollback.sql','APPLIED',
'Own33564/33567 same current vehicle10059-driver1/crosszone sameinstant/late rollback/concurrent HTTP one200-one409/version loser unchanged/exact endstart accepted. Initial503 Oracle04068 slowlog2037, pooled API restart/same source fixtures reused. Peer cancelled/history retained/no goods/protected20-20. NativeVALID; legal actual driver/warehouse admission remains.');
commit;
