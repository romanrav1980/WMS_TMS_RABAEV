create or replace trigger RRL_WH_FINAL_SCALE_USE_GUARD before insert or update or delete on RRL_WH_FINAL_SCALE_USE for each row
declare wire clob;plan clob;command_value varchar2(50);state_value varchar2(20);d json_object_t;dom json_object_t;
begin
 if not inserting then raise_application_error(-20863,'FINAL_SCALE_USE_IMMUTABLE');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=:new.STOCK_OPERATION_ID
  then raise_application_error(-20863,'FINAL_SCALE_ROOT_TRANSACTION_REQUIRED');end if;
 select CANONICAL_REQUEST,RESOLVED_PLAN_JSON,COMMAND_TYPE,STATE into wire,plan,command_value,state_value from RRL_STOCK_OPERATION where OPERATION_ID=:new.STOCK_OPERATION_ID;
 d:=json_object_t.parse(wire);dom:=json_object_t.parse(plan).get_object('domain');
 if command_value!='OUTGOING_PALLET_CHECK'or state_value!='IN_FLIGHT'or d.get_string('actor')!=:new.ACTOR
  or d.get_object('metadata').get_string('final_scale_capture')is null or d.get_object('metadata').get_string('final_scale_capture')!=:new.CAPTURE_KEY
  or dom.get_number('case_task')!=:new.CASE_PICK_TASK_ID or dom.get_number('case_version')!=:new.CASE_CONTENT_VERSION
  or dom.get_object('quality').get_string('composition_signature')!=:new.COMPOSITION_SIGNATURE
  or dom.get_object('quality').get_number('composition_signature_version')is null or dom.get_object('quality').get_number('composition_signature_version')!=:new.SIGNATURE_VERSION
  then raise_application_error(-20863,'FINAL_SCALE_ORIGINAL_QC_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','WH.FINAL.SCALE.USE:'||:new.CAPTURE_KEY));
end;
/
