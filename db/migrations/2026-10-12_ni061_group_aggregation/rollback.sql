@000_before_group_rec.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-667-group-aggregation-receiving';
/
