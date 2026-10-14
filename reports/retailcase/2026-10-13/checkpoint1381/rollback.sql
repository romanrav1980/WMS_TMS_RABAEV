-- MIGRATION_ID: 2026-10-14-1381-st-page-keys
-- Only this additive index is removed. No business history is deleted.
drop index RRL_ST_PAGE_KEYS_I;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-1381-st-page-keys';
commit;