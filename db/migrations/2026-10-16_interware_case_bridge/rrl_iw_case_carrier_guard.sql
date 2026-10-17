create or replace trigger RRL_IW_CASE_CARRIER_GUARD before insert or update or delete on RRL_IW_CASE_CARRIER for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');wire clob;kind_value varchar2(80);state_value varchar2(20);n number;cell_value varchar2(60);source_value varchar2(100);ware_value number;
begin
 if not inserting or op is null or op!=:new.RECEIPT_OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then
  raise_application_error(-20863,'INTERWARE_CASE_ORIGIN_IMMUTABLE_ROOT_ONLY');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_value,state_value,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
 cell_value:=json_object_t.parse(wire).get_object('domain').get_string('receive_cell');source_value:=json_object_t.parse(wire).get_object('domain').get_string('source_load_operation_id');ware_value:=json_object_t.parse(wire).get_object('domain').get_number('warehouse_id');
 select count(*)into n from json_table(wire,'$.domain.nested_source.received_cases[*]'columns(U varchar2(200)path '$.carrier_uid',C number path '$.case_task_id',S varchar2(64)path '$.pallet_identifier',V number path '$.source_case_version',W number path '$.source_warehouse_id',J clob format json path '$'))j
  where j.U=:new.CARRIER_UID and j.C=:new.CASE_TASK_ID and j.S=:new.PALLET_IDENTIFIER and j.V=:new.SOURCE_CASE_VERSION and j.W=:new.SOURCE_WARE_ID and json_equal(j.J,:new.SOURCE_JSON);
 if kind_value!='INTERWARE_RECEIVE'or state_value!='IN_FLIGHT'or n!=1 or source_value!=:new.SOURCE_LOAD_OPERATION_ID or ware_value!=:new.TARGET_WARE_ID
  or :new.CREATED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'INTERWARE_CASE_ORIGIN_EXACT_PLAN_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(:new.CASE_TASK_ID)));
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.CARRIER_UID));
end;
/
