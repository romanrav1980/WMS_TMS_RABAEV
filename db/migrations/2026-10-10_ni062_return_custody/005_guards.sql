create or replace trigger RRL_TRANSPORT_DRIVER_USER_GUARD before insert or update or delete on RRL_TRANSPORT_DRIVER_USER for each row
declare n number;
begin
 if deleting then raise_application_error(-20863,'DRIVER_BINDING_DEACTIVATE_REQUIRED');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='CONFIG' or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION') is null or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION')!='warehouse_settings_edit'
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'DRIVER_EXPLICIT_CONFIGURATION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*) into n from RRL_TR_VODITEL where ID=:new.DRIVER_ID and nvl(DELETED,0)=0;
 if n!=1 then raise_application_error(-20886,'DRIVER_SINGLE_ACTIVE_LEGACY_ID_REQUIRED');end if;
 if :new.ACTIVE=1 then
  select count(*) into n from RUSERS where ID=:new.USER_ID and nvl(DELETED,0)=0 and upper(trim(USER_GROUP))!='GLOBAL_ADMIN' and RRL_HAS_WRIGHT(ID,'driver_return_accept')=1;
  if n!=1 then raise_application_error(-20882,'DRIVER_DEDICATED_ACTIVE_USER_REQUIRED');end if;
 end if;
 if inserting and :new.BINDING_VERSION!=1 then raise_application_error(-20863,'DRIVER_INITIAL_BINDING_VERSION_REQUIRED');end if;
 if updating and(:new.DRIVER_ID!=:old.DRIVER_ID or :new.BINDING_VERSION!=:old.BINDING_VERSION+1)then raise_application_error(-20863,'DRIVER_BINDING_VERSION_REQUIRED');end if;
 if :new.CHANGED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR') then raise_application_error(-20863,'DRIVER_CONFIG_ACTOR_REQUIRED');end if;
end;
/
create or replace trigger RRL_STORE_RETURN_HAND_GUARD before insert or update or delete on RRL_STORE_RETURN_HANDOVER for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'STORE_RETURN_CUSTODY_HISTORY_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RETURN_CUSTODY_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RETURN_HANDOVER' or v_state!='IN_FLIGHT' then raise_application_error(-20863,'STORE_RETURN_CUSTODY_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_HANDOVER',op));
end;
/
create or replace trigger RRL_STORE_RETURN_PICK_GUARD before insert or update or delete on RRL_STORE_RETURN_PICKUP for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'STORE_RETURN_CUSTODY_HISTORY_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RETURN_CUSTODY_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RETURN_PICKUP' or v_state!='IN_FLIGHT' then raise_application_error(-20863,'STORE_RETURN_CUSTODY_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_PICKUP',op));
end;
/
