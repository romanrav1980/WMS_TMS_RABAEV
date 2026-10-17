@@before.sql
@@body.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME='RRL_WH_WEIGH_REQUEST_API';
 if n!=0 then raise_application_error(-20886,'WH_REQUEST_SQL_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'WH_REQUEST_SQL_GLOBAL_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-warehouse-scale-request-sql-boundary'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Bounded pure SQL scalar JSON extraction, no PL/SQL JSON object crossing SQL',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
