-- Keep camera configuration, incident review versions and immutable existing CASE events.
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-028-short-investigation';
commit;
/
