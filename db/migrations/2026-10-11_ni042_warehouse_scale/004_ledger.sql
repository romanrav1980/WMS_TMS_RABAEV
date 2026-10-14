merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-187-warehouse-scale-archive'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Addressed warehouse scale immutable archive, dedicated current warehouse sender, existing CASE/version source, shared stability reader',sysdate,user,
'db/migrations/2026-10-11_ni042_warehouse_scale/apply.sql','db/migrations/2026-10-11_ni042_warehouse_scale/rollback.sql','APPLIED',
'Own CASE1060 actual API TEST device stable gross10.1/raw SHA/current warehouse/scans/version/exact replay/conflict/unstable/admin-sender403/read permission/append-only/no stock; current independent source scope; quality544/0/76/24/bothTS PASS; once-only stock consumption next');
commit;
