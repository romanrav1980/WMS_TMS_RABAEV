merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-273-exact-sap-source-scope'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'SAP supply source current scope and original exact Oracle conversion',sysdate,user,
'db/migrations/2026-10-11_ni011_exact_source/apply.sql','db/migrations/2026-10-11_ni011_exact_source/rollback.sql','APPLIED',
'Native source scope supplypermission/sharedCFG4/exact native rational1-3/store144-48 supply3-1/fractionpiece refusal/currentcached WARE-rights denials/actorrestored/HTTP/noStock/P20H20/nativeVALID. GlobalSRX remains next incremental improvement.');
commit;
