@@070_shipping_legacy_checkpoint.sql
@@070_shipping_entrypoints.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_CLOSE_OTHOD_NAKLAD','RRL_CLOSE_OTHOD_PALLET','RRL_CLOSE_OTHOD_NAKLAD_SP_OLD','RRL_CLOSE_OTHOD_PALLET_SP_OLD') and OBJECT_TYPE='FUNCTION' and STATUS='VALID';
 if n!=4 then raise_application_error(-20808,'SHIPPING_ENTRYPOINTS_NOT_VALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-029-shipping-entrypoints' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing outgoing document/pallet entrypoints use stock coordinator on global activation; legacy fallback PREPARED',sysdate,user,'070_shipping_entrypoints_apply.sql','070_shipping_entrypoints_rollback.sql','APPLIED');
commit;
