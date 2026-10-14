@@000_before_rules_package_body.sql
@@000_before_rrl_stock_hu_load_core.sql
@@000_before_rrl_stock_trip_depart_cmd.sql
drop package RRL_STORE_ACCESS_RULES;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-14-ni022-store-access-dimensions';
commit;
/
