alter table RRL_CASE_PICK_SHORT modify CREATED_AT_INSTANT default null;
-- Keep captured instants and old nullable rows; deploy matching earlier archive reader.
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-037-incident-instants';
commit;
/
