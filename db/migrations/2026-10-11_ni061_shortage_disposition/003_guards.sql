create or replace package RRL_IW_SHORTAGE_GUARD authid definer as
 procedure require_command(p_operation varchar2,p_kind varchar2);
end;
/
create or replace package body RRL_IW_SHORTAGE_GUARD as
 procedure require_command(p_operation varchar2,p_kind varchar2)is n number;begin
 if p_operation is null or p_operation!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_SHORTAGE_NATIVE_TRANSACTION_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=p_operation and STATE='IN_FLIGHT'and COMMAND_TYPE=p_kind;
 if n!=1 then raise_application_error(-20863,'INTERWARE_SHORTAGE_CAPTURED_COMMAND_REQUIRED');end if;
 end;
end;
/
create or replace trigger RRL_IW_SHORT_REQUEST_G before insert or update or delete on RRL_INTERWARE_SHORTAGE_REQUEST for each row
begin
 if updating or deleting then raise_application_error(-20863,'INTERWARE_SHORTAGE_HISTORY_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'INTERWARE_SHORTAGE_REPORT');
end;
/
create or replace trigger RRL_IW_SHORT_FACT_G before insert or update or delete on RRL_INTERWARE_SHORTAGE_FACT for each row
begin
 if updating or deleting then raise_application_error(-20863,'INTERWARE_SHORTAGE_HISTORY_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'INTERWARE_SHORTAGE_CONFIRM');
end;
/
create or replace trigger RRL_IW_SHORT_UNIT_G before insert or update or delete on RRL_INTERWARE_SHORTAGE_UNIT for each row
begin
 if updating or deleting then raise_application_error(-20863,'INTERWARE_SHORTAGE_HISTORY_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.FACT_OPERATION_ID,'INTERWARE_SHORTAGE_CONFIRM');
 RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',:new.PHYSICAL_UNIT_KEY));
end;
/
