prompt Preserve original deadline on urgent residual warehouse step
@@001_task_core.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_TASK_CORE' and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'RESIDUAL_DEADLINE_PACKAGE_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-018-residual-deadline' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Urgent residual preserves original deadline; resource assignment and ordinary planning dates cleared',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
