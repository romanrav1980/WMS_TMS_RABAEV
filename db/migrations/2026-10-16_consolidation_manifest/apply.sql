@@before.sql
@@tables.sql
@@rrl_hu_consol_read_package.sql
@@rrl_hu_consol_read_package_body.sql
@@rrl_hu_consol_api_package.sql
@@rrl_hu_consol_api_package_body.sql
@@triggers.sql
@@rrl_stock_hu_ship_cmd_package_body.sql
@@compile_dependents.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-consolidation-manifest','Expected consolidation metadata and native shipping guard',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
