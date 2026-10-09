declare n number;
begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in(
 'RRL_STOCK_UNIT_CORE','RRL_STOCK_RESERVATION_CMD','RRL_STOCK_RECEIPT_PLAN','RRL_STOCK_RECEIPT_CORE','RRL_STOCK_CONFIG_API')
 and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=10 then raise_application_error(-20808,'DOMAIN_HANDLERS_NOT_VALID');end if;
 select count(*) into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='PREPARED';
 if n!=1 then raise_application_error(-20808,'DORMANT_INSTALL_STATE_CHANGED');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(
 select '2026-10-08-018-stock-reservation-commands' MIGRATION_ID,'041_reservations_apply.sql' SCRIPT_NAME,'041_reservations_rollback.sql' ROLLBACK_SCRIPT from dual
 union all select '2026-10-08-019-stock-receipt-command','046_receipt_apply.sql','046_receipt_rollback.sql' from dual
 union all select '2026-10-08-020-stock-configuration-fence','048_configuration_apply.sql','048_configuration_rollback.sql' from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant domain adapter; PREPARED, no physical commands or cutover',sysdate,user,s.SCRIPT_NAME,s.ROLLBACK_SCRIPT,'APPLIED');
commit;
