create or replace trigger RRL_TT_UNLOAD_FACT_GUARD before insert or update or delete on RRL_TT_UNLOAD_FACT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);state_name varchar2(20);wire clob;v json_object_t;
begin
 if not inserting then raise_application_error(-20863,'UNLOAD_FACT_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'UNLOAD_NATIVE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_name,state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind_name!='UNLOAD_SHIPMENT'or state_name!='IN_FLIGHT'then raise_application_error(-20863,'UNLOAD_NATIVE_ROOT_REQUIRED');end if;
 v:=json_object_t.parse(wire).get_object('domain');
 if v.get_string('load_id')!=:new.LOAD_OPERATION_ID or v.get_number('trip_id')!=:new.TT_ID or v.get_number('case_id')!=:new.CASE_PICK_TASK_ID or v.get_number('warehouse')!=:new.WARE_ID
  or v.get_object('snapshot').get_string('cell')!=:new.CELL_CODE or dbms_lob.compare(v.get_object('snapshot').to_clob,:new.COMPOSITION_JSON)!=0 then raise_application_error(-20863,'UNLOAD_SOURCE_PLAN_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_UNLOAD_FACT',op));
end;
/
