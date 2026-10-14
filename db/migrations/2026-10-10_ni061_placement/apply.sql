@@001_schema.sql
@@002_command.sql
@@003_task_plan.sql
@@004_task_core.sql
@@005_task_domain.sql
@@006_root.sql
@@007_guards.sql
declare n number;begin select count(*)into n from user_objects where OBJECT_NAME in('RRL_STOCK_INTERWARE_PUT','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE','RRL_STOCK_TASK_DOMAIN','RRL_STOCK_POSTING_API','RRL_INTERWARE_PUT_GUARD','RRL_INTERWARE_PLACEMENT_GUARD')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'INTERWARE120_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-120-interwarehouse-existing-placement-task' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing MANUAL PUTAWAY task for whole original interwarehouse receipt to existing target trip dock; native stock movement',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
