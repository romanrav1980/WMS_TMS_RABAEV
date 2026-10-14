create or replace trigger RRL_TT_HU_LOAD_ST_GUARD before insert or update or delete on RRL_TT_HU_LOAD_ST for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);state_name varchar2(20);n number;source_load varchar2(100);
begin
 if deleting then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBERS_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'PHYSICAL_LOAD_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_name,state_name from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if state_name!='IN_FLIGHT'then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBER_SHIPMENT_REQUIRED');end if;
 if inserting then
  if kind_name not in('HU_SHIP','LOAD_SHIPMENT','RECONCILE_HU_LOAD')or :new.LOAD_OPERATION_ID!=op or :new.DESTINATION_ADDR is null then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBER_SHIPMENT_REQUIRED');end if;
  source_load:=op;
 else
  source_load:=:old.LOAD_OPERATION_ID;
  if kind_name!='UNLOAD_SHIPMENT'or :old.ACTIVE_FLAG!=1 or :new.ACTIVE_FLAG!=0 or :new.LOAD_OPERATION_ID!=:old.LOAD_OPERATION_ID or :new.SBORKA_PALLET_ID!=:old.SBORKA_PALLET_ID or nvl(:new.DESTINATION_ADDR,chr(0))!=nvl(:old.DESTINATION_ADDR,chr(0))then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBERS_IMMUTABLE');end if;
  select count(*)into n from RRL_TT_UNLOAD_FACT u join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=u.LOAD_OPERATION_ID where u.OPERATION_ID=op and u.LOAD_OPERATION_ID=source_load and lf.STATUS='UNLOADED';
  if n!=1 then raise_application_error(-20863,'UNLOAD_IMMUTABLE_PROOF_REQUIRED');end if;
 end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_HU_LOAD_ST',source_load||':'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.SBORKA_PALLET_ID)));
end;
/
