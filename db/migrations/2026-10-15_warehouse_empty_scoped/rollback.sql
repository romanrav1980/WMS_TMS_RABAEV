-- Quiesce queue/capture/metadata writers. Any new durable weighing history requires forward recovery.
@@after_source_guard.sql
@@history_baseline_guard.sql
@@before_rrl_case_resource_policy_package_body.sql
@@before_rrl_wh_weigh_request_api_package_body.sql
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-warehouse-empty-scoped';
commit;
