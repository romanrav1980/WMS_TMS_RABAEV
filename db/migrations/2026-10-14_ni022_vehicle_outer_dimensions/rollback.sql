-- Restore owner implementation; retain additive nullable columns/history (no evidence deletion).
@@000_before_body.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-14-ni022-vehicle-outer-dimensions';
commit;
/
