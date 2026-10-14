merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-209-case-issued-route-sequence'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Enforce original issued CASE linear route under same native CASE lock',sysdate,user,
'db/migrations/2026-10-11_ni042_route_sequence/apply.sql','db/migrations/2026-10-11_ni042_route_sequence/rollback.sql','APPLIED',
'Own CASE1106/wave460/two physical cells/ranks1then2/source4/picked2: ahead409,no stock; facefuture99 leaves issued1; both native picks/replay/close rollback. Cleanup exact original cells/native stock0/protected13520/20. All-null legacy DIRECT retained; laying-stage validation remains.');
commit;
