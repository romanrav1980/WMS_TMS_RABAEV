-- Disable HTTP composition and quiesce metadata writers first. Never delete close history.
@@known_sources_guard_raw.sql
@@after_source_guard.sql
@@journal_baseline_guard.sql
drop package RRL_CASE_LIFECYCLE_API;
@@rollback_verify_v2.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-case-scoped-close';
commit;
