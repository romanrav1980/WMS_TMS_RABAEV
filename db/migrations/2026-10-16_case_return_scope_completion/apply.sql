@@before.sql
@@rrl_case_task_access_package_body.sql
@@after.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-case-return-scope','Original bodies verified; one body repaired by compile completion',sysdate,user,'apply.sql','FORWARD_ONLY','APPLIED');
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-case-return-scope-completion','Repair inspected LOT physical cell join; preserve failure artifacts',sysdate,user,'apply.sql','FORWARD_ONLY','APPLIED');
commit;
