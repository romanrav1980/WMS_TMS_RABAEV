-- MIGRATION_ID: 2026-10-15-transport-scoped-edit
@@rrl_transport_plan_rules.sql
@@rrl_transport_edit_api.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-transport-scoped-edit' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Scoped dispatcher edit; pure preflight authority; guarded command revision',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
