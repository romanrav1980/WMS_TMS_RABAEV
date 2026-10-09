create or replace trigger RRL_STOCK_COMPAT_FLAG_GUARD
 before insert or update or delete on RRL_SYSTEM_SETTINGS for each row
begin
 if nvl(:new.SETTING_KEY,:old.SETTING_KEY)!='STOCK_LEGACY_TRIGGER_ENABLED'
  and nvl(:old.SETTING_KEY,:new.SETTING_KEY)!='STOCK_LEGACY_TRIGGER_ENABLED' then return;end if;
 if deleting or (updating and :old.SETTING_KEY!=:new.SETTING_KEY) then raise_application_error(-20863,'COMPATIBILITY_SETTING_DELETE_FORBIDDEN');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='CONFIG'
  or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION') is null or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION')!='stock_compatibility_admin'
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or :new.SETTING_VALUE is null or :new.SETTING_VALUE not in('0','1') then raise_application_error(-20863,'COMPATIBILITY_SETTING_COMMAND_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK'),6);
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
end;
/
create or replace trigger RRL_STOCK_SETTING_AUDIT_GUARD
 before insert or update or delete on RRL_STOCK_SETTING_AUDIT for each row
begin
 if updating or deleting then raise_application_error(-20863,'SETTING_AUDIT_IMMUTABLE');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION') is null or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION')!='stock_compatibility_admin'
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'SETTING_AUDIT_COMMAND_REQUIRED');end if;
end;
/
