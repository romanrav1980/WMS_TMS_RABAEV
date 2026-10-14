@@001_access_helper.sql
@@002_plan_rules.sql
@@003_load.sql
@@004_depart.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-ni022-store-access-dimensions' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Single native store outer vehicle access check for planning, load and departure',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
