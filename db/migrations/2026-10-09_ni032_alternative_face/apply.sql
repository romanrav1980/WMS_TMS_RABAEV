@@001_schema.sql
@@002_capacity.sql
@@003_eligibility.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_REPL_CAPACITY','RRL_STOCK_ELIGIBILITY') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=4 then raise_application_error(-20808,'DYNAMIC_FACE_POLICY_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-039-alternative-pick-face' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Reuse dynamic face assignments with frozen BASE volume and durable row source intents',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
