prompt Recompilation did not change source; there is no semantic source rollback
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-08-014b-stock-dependent-compilation';
commit;
