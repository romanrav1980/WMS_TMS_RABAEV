-- Retain cycle history. Deploy matching preceding API before reverting.
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-024-minimax-cycle';
commit;
/
