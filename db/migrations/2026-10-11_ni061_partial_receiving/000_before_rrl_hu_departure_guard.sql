
  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_HU_DEPARTURE_GUARD" before insert or update of HU_SHIPPED_OPERATION on RRL_PALLETS for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind varchar2(80);begin
 if inserting and :new.HU_SHIPPED_OPERATION is null then return;end if;
 if updating and nvl(:new.HU_SHIPPED_OPERATION,chr(0))=nvl(:old.HU_SHIPPED_OPERATION,chr(0)) then return;end if;
 if op is not null and sys_context('RRL_STOCK_WRITE_CTX','TX_ID')=dbms_transaction.local_transaction_id(false)then
  select COMMAND_TYPE into kind from RRL_STOCK_OPERATION where OPERATION_ID=op;
  if kind='UNLOAD_SHIPMENT'then
   if not updating or :old.HU_SHIPPED_OPERATION is null or :new.HU_SHIPPED_OPERATION is not null or :new.HU_CURRENT_CELL is null or :new.HU_KIND!='CONTAINER'then raise_application_error(-20863,'UNLOAD_CONTAINER_REVERSE_ONLY');end if;
   declare wire clob;n number;load_id varchar2(100);state_name varchar2(20);cell_text varchar2(60);begin
    select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
    load_id:=json_object_t.parse(wire).get_object('domain').get_string('load_id');cell_text:=json_object_t.parse(wire).get_object('domain').get_object('snapshot').get_string('cell');
    select count(*)into n from json_table(wire,'$.domain.snapshot.nodes[*]'columns(U varchar2(150)path '$.uid',K varchar2(20)path '$.kind',V number path '$.version'))j where j.U=:new.UID_PALLET and j.K='CONTAINER'and j.V+1=:old.HU_CONTENT_VERSION;
    if state_name!='IN_FLIGHT'or n!=1 or load_id!=:old.HU_SHIPPED_OPERATION or cell_text!=:new.HU_CURRENT_CELL or :new.HU_CONTENT_VERSION!=:old.HU_CONTENT_VERSION+1 then raise_application_error(-20863,'UNLOAD_CONTAINER_ORIGINAL_LOAD_REQUIRED');end if;
   end;
   RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));return;
  end if;
 end if;
 if op is null or :new.HU_SHIPPED_OPERATION!=op or :new.HU_KIND!='CONTAINER' or :new.HU_CURRENT_CELL is not null
  or :old.HU_SHIPPED_OPERATION is not null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_DEPARTURE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE into kind from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind!='HU_SHIP' then raise_application_error(-20863,'HU_DEPARTURE_COMMAND_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
end;

ALTER TRIGGER "RABAEV"."RRL_HU_DEPARTURE_GUARD" ENABLE
