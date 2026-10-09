declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_BALANCE_CORE','RRL_STOCK_EFFECT_CORE','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=8 then raise_application_error(-20808,'SHIPPING_PACKAGES_NOT_VALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-028-shipping-command' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Atomic document shipment; exact FEFO free-stock allocation; no fabricated MINUS/EXCESS; legacy document journal links',sysdate,user,'069_shipping_apply.sql','069_shipping_rollback.sql','APPLIED');
commit;
