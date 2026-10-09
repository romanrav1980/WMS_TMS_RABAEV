prompt Durable confirmation on existing warehouse tasks; no new task/stock registry
declare n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 select count(*) into n from user_tab_columns where table_name='RRL_WAREHOUSE_TASK' and column_name='COMPLETION_HASH';
 if n=0 then execute immediate 'alter table RRL_WAREHOUSE_TASK add (COMPLETION_HASH varchar2(64),COMPLETION_JSON clob)'; end if;
 select count(*) into n from user_constraints where constraint_name='RRL_WH_TASK_COMPLETION_JSON';
 if n=0 then execute immediate 'alter table RRL_WAREHOUSE_TASK add constraint RRL_WH_TASK_COMPLETION_JSON check(COMPLETION_JSON is json)'; end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-07-010-ni03-task-effect' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing warehouse task atomic completion and durable request identity',sysdate,user,'010_apply.sql','010_rollback.sql','APPLIED');
commit;