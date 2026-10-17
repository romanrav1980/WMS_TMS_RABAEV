@@before.sql
@@schema.sql
@@rrl_iw_case_bridge_package.sql
@@rrl_iw_case_bridge_package_body.sql
@@rrl_iw_group_archive_package_body.sql
@@rrl_iw_group_rec_package_body.sql
@@rrl_iw_hu_rec_core_package_body.sql
@@rrl_stock_hu_read_package_body.sql
@@rrl_hu_container_guard_trigger.sql
@@rrl_iw_case_carrier_guard.sql
@@compile_dependents.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-interware-case-bridge','Guarded package-only increment; see frozen manifest and wiki',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
