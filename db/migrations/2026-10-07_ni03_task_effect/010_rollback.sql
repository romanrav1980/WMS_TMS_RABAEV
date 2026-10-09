declare n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 select count(*) into n from RRL_WAREHOUSE_TASK where COMPLETION_HASH is not null;
 if n>0 then raise_application_error(-20802,'Confirmed warehouse facts require export and explicit recovery; rollback refused'); end if;
 execute immediate 'alter table RRL_WAREHOUSE_TASK drop constraint RRL_WH_TASK_COMPLETION_JSON';
 execute immediate 'alter table RRL_WAREHOUSE_TASK drop (COMPLETION_HASH,COMPLETION_JSON)';
 delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-07-010-ni03-task-effect';
end;
/
commit;