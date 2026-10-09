declare n number;
begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in
 ('RRL_STOCK_PALLET_UOM','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE')
 and OBJECT_TYPE in ('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=6 then raise_application_error(-20808,'PALLET_UOM_PACKAGES_NOT_VALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using
 (select '2026-10-08-025-pallet-exact-uom' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Dormant task UOM uses actual pallet MOD_ID; exact arithmetic and replan signature',sysdate,user,'063_pallet_uom_apply.sql','063_pallet_uom_rollback.sql','APPLIED');
commit;
