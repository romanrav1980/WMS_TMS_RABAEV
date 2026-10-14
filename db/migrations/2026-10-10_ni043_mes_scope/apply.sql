@@001_core.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_MES_MOVEMENT_CORE'and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'MES127_INVALID_CORE');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-127-mes-current-warehouse-scope' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Current MES actor warehouse scope enforced inside existing sole native stock writer',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
