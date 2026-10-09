declare n number;s varchar2(20);begin
 select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if s!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_SHIPPING_CORE','RRL_STOCK_CASE_PICK_CMD','RRL_STOCK_CASE_MOVE_CMD') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'CASE_SHIPMENT_OBJECT_INVALID');end if;
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_CASE_SHIPMENT_UK' and STATUS='ENABLED' and VALIDATED='VALIDATED';
 if n!=1 then raise_application_error(-20808,'CASE_SHIPMENT_UNIQUENESS_REQUIRED');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-001-case-existing-st-shipment' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Bind physical CASE carrier to existing ST; exact whole-carrier shipment and shared transaction',
 sysdate,user,'202_case_shipment_apply.sql','201_case_shipment_rollback.sql','APPLIED');
commit;
