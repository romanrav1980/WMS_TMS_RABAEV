@@001_config.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_CONFIG_API','RRL_STOCK_POSTING_API')and STATUS!='VALID';
 if n!=0 then raise_application_error(-20899,'PICKFACE142_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-142-atomic-existing-pickface-config' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Existing pick topology edit behind configuration fence; atomic existing article slot settings',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
