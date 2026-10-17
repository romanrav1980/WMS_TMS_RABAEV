@@before.sql
@@rrl_full_shipping_scope_package.sql
@@rrl_full_shipping_scope_package_body.sql
@@rrl_stock_hu_ship_cmd_package_body.sql
@@rrl_stock_trip_depart_cmd_package_body.sql
@@rrl_stock_shipping_core_package_body.sql
@@rrl_stock_posting_api_package_body.sql
@@compile_dependents.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-full-shipping-scope','Guarded package-only increment; see frozen manifest and wiki',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
