merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-212-standalone-case-unload' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Native standalone CASE unload before departure with restored original stock and HARD',sysdate,user,
'db/migrations/2026-10-11_ni052_unload/apply.sql','db/migrations/2026-10-11_ni052_unload/rollback.sql','APPLIED',
'Actual CASE1113/wave467/original load-6 retained/unload+6/P6H6; late rollback and concurrent one winner, replay/current wrong warehouse403. Shipping history immutable/control revoked/native cleanupP0H0/protected13520/20. Nested cargo, captured units and transferred tare require explicit extension.');
commit;
