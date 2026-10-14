create or replace trigger RRL_TARE_POLICY_GUARD before insert or update or delete on RRL_TARE_RETURN_POLICY for each row
declare n number;v_key varchar2(255);v_tz timestamp with time zone;
begin
 if deleting then raise_application_error(-20863,'TARE_POLICY_PRESERVE_HISTORY_REQUIRED');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='CONFIG' or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION') is null or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION')!='warehouse_settings_edit'
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'TARE_POLICY_EXPLICIT_CONFIG_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if :new.SCOPE_KIND='CUSTOMER' then
 select count(*) into n from RRL_CUSTOMER where to_char(CUSTOMER_ID,'TM9')=:new.SCOPE_KEY and ACTIVE=1;
 else select count(*) into n from RRL_CUSTOMER_STORE_MAP where LEGACY_ADDR=:new.SCOPE_KEY and ACTIVE=1;
  if n=0 then select count(*) into n from RRL_SBORKA_PALLETS where ADDR=:new.SCOPE_KEY;end if;
 end if;
 if n=0 then raise_application_error(-20886,'TARE_KNOWN_ACTIVE_STORE_OR_CUSTOMER_REQUIRED');end if;
 begin v_tz:=from_tz(cast(systimestamp as timestamp),:new.TIMEZONE_REGION);
 exception when others then raise_application_error(-20886,'TARE_VALID_TIMEZONE_REGION_REQUIRED');end;
 if inserting and :new.POLICY_VERSION!=1 then raise_application_error(-20863,'TARE_INITIAL_POLICY_VERSION_REQUIRED');end if;
 if updating and(:new.SCOPE_KIND!=:old.SCOPE_KIND or :new.SCOPE_KEY!=:old.SCOPE_KEY or :new.POLICY_VERSION!=:old.POLICY_VERSION+1)then raise_application_error(-20863,'TARE_POLICY_IDENTITY_VERSION_REQUIRED');end if;
 if :new.CHANGED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TARE_POLICY_ACTOR_REQUIRED');end if;
end;
/
create or replace trigger RRL_TARE_DELIVERY_POLICY_GUARD before insert or update or delete on RRL_TARE_DELIVERY_POLICY for each row
begin
 if not inserting then raise_application_error(-20863,'TARE_DELIVERY_POLICY_HISTORY_IMMUTABLE');end if;
 if :new.ACCEPT_OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_ROOT_OPERATION_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_DELIVERY_POLICY',:new.ACCEPT_OPERATION_ID,'TARE_ACCEPT');
end;
/
