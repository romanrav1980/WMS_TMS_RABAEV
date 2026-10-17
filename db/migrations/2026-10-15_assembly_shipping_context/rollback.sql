-- Quiesce readers; restore paired exact before body.
@@before_body.sql
@@verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-assembly-shipping-context';
commit;
