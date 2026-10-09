declare n number;s varchar2(20);begin
 select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if s!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_RESERVE_CORE','RRL_STOCK_TRANSFER_CORE') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'CASE_ALLOCATION_OBJECT_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-002-case-allocation-eligibility' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Prevent fresh allocation/foreign merge of stock packed into physical CASE carrier',
 sysdate,user,'206_case_allocation_guard_apply.sql','206_case_allocation_guard_rollback.sql','APPLIED');
commit;
