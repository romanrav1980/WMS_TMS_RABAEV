-- Retain schedule/history metadata; revert matching API before disabling planning.
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-026-reach-shifts';
commit;
/
