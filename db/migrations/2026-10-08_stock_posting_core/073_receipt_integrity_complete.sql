declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME like 'RRL_STOCK_%' and OBJECT_TYPE in('PACKAGE','PACKAGE BODY','TRIGGER') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'STOCK_COMPONENTS_NOT_VALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-030-receipt-pallet-integrity' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Pallet split provenance/mass, physical receipt unit admission, SAP receipt outbox, blocked receiving source and authorized whole quarantine move, exact UOM config publication',sysdate,user,'073_receipt_integrity_apply.sql','073_receipt_integrity_rollback.sql','APPLIED');
commit;
