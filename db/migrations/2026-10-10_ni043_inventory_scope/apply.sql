@@001_birth.sql
@@002_count.sql
alter package RRL_STOCK_POSTING_API compile body;
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_INVENTORY_BIRTH','RRL_STOCK_INVENTORY_CMD','RRL_STOCK_POSTING_API')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'INVENTORY129_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-129-inventory-current-warehouse-scope' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Current warehouse actor scope inside native inventory birth/count; existing sole posting kernel',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
