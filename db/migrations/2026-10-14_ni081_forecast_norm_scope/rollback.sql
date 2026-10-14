@@000_before_body.sql
-- Keep configuration history and guarded table; do not delete business decisions.
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-14-1328-forecast-norm-scope';
/
