@@001_api.sql
@@002_history_guard.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TT_OPERATION_PLAN_API','RRL_TT_OP_EXECUTION_GUARD','RRL_STOCK_POSTING_API')and STATUS!='VALID';
 if n!=0 then raise_application_error(-20899,'OP_PLAN141_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-141-preserve-operation-execution' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Reuse original ARM norms/operations without deleting execution history; current actor/source and same-TX plan',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
