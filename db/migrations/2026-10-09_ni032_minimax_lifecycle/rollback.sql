-- Deploy the preceding API before reverting. Retain intent/history column.
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-023-minimax-lifecycle';
commit;
/
