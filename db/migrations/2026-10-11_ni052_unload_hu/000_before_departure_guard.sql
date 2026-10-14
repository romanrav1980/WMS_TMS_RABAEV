create or replace trigger RRL_HU_DEPARTURE_GUARD before insert or update of HU_SHIPPED_OPERATION on RRL_PALLETS for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind varchar2(80);begin
 if inserting and :new.HU_SHIPPED_OPERATION is null then return;end if;
 if updating and nvl(:new.HU_SHIPPED_OPERATION,chr(0))=nvl(:old.HU_SHIPPED_OPERATION,chr(0)) then return;end if;
 if op is null or :new.HU_SHIPPED_OPERATION!=op or :new.HU_KIND!='CONTAINER' or :new.HU_CURRENT_CELL is not null
  or :old.HU_SHIPPED_OPERATION is not null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_DEPARTURE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE into kind from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind!='HU_SHIP' then raise_application_error(-20863,'HU_DEPARTURE_COMMAND_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
end;
/
