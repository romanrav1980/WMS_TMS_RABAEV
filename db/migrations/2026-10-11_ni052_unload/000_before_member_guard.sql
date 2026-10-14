create or replace trigger RRL_TT_HU_LOAD_ST_GUARD before insert or update or delete on RRL_TT_HU_LOAD_ST for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);state_name varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBERS_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'PHYSICAL_LOAD_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_name,state_name from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind_name not in('HU_SHIP','LOAD_SHIPMENT','RECONCILE_HU_LOAD') or state_name!='IN_FLIGHT' or :new.LOAD_OPERATION_ID!=op or :new.DESTINATION_ADDR is null then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBER_SHIPMENT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_HU_LOAD_ST',op||':'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.SBORKA_PALLET_ID)));
end;
/
