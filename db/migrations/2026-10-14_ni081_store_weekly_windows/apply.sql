-- MIGRATION_ID: 2026-10-14-ni081-store-weekly-windows
-- Root applies only after store-profile and vehicle-outer-dimensions dependencies.
@@001_window_rules.sql
@@002_route_schedule.sql
@@003_time_snapshot.sql
@@verify.sql
@@selftest.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-ni081-store-weekly-windows' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Native weekly store windows and current store/fleet snapshot V7; no stock changes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
