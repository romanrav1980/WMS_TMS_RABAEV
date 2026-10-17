create or replace trigger RRL_ASM_STATION_GUARD before insert or update or delete on RRL_ASSEMBLY_STATION for each row
begin
 if deleting then raise_application_error(-20886,'ASSEMBLY_HISTORY_DELETE_FORBIDDEN');end if;
 if RRL_ASSEMBLY_SCALE_API.write_allowed('POLICY')!=1 then raise_application_error(-20882,'ASSEMBLY_NATIVE_CONTEXT_REQUIRED');end if;
end;
/

create or replace trigger RRL_ASM_SKU_POLICY_GUARD before insert or update or delete on RRL_ASSEMBLY_SKU_POLICY for each row
begin
 if deleting then raise_application_error(-20886,'ASSEMBLY_HISTORY_DELETE_FORBIDDEN');end if;
 if RRL_ASSEMBLY_SCALE_API.write_allowed('POLICY')!=1 then raise_application_error(-20882,'ASSEMBLY_NATIVE_CONTEXT_REQUIRED');end if;
end;
/

create or replace trigger RRL_ASM_POLICY_EVENT_GUARD before insert or update or delete on RRL_ASSEMBLY_POLICY_EVENT for each row
begin
 if not inserting then raise_application_error(-20886,'ASSEMBLY_APPEND_ONLY');end if;
 if RRL_ASSEMBLY_SCALE_API.write_allowed('POLICY')!=1 then raise_application_error(-20882,'ASSEMBLY_NATIVE_CONTEXT_REQUIRED');end if;
end;
/

create or replace trigger RRL_ASM_SESSION_GUARD before insert or update or delete on RRL_ASSEMBLY_SESSION for each row
begin
 if deleting then raise_application_error(-20886,'ASSEMBLY_HISTORY_DELETE_FORBIDDEN');end if;
 if RRL_ASSEMBLY_SCALE_API.write_allowed('STATE')!=1 then raise_application_error(-20882,'ASSEMBLY_NATIVE_CONTEXT_REQUIRED');end if;
end;
/

create or replace trigger RRL_ASM_STEP_GUARD before insert or update or delete on RRL_ASSEMBLY_STEP for each row
begin
 if deleting then raise_application_error(-20886,'ASSEMBLY_HISTORY_DELETE_FORBIDDEN');end if;
 if RRL_ASSEMBLY_SCALE_API.write_allowed('STATE')!=1 then raise_application_error(-20882,'ASSEMBLY_NATIVE_CONTEXT_REQUIRED');end if;
end;
/

create or replace trigger RRL_ASM_CAPTURE_GUARD before insert or update or delete on RRL_ASSEMBLY_CAPTURE for each row
begin
 if not inserting then raise_application_error(-20886,'ASSEMBLY_APPEND_ONLY');end if;
 if RRL_ASSEMBLY_SCALE_API.write_allowed('CAPTURE')!=1 then raise_application_error(-20882,'ASSEMBLY_NATIVE_CONTEXT_REQUIRED');end if;
end;
/

create or replace trigger RRL_ASM_STEP_USE_GUARD before insert or update or delete on RRL_ASSEMBLY_STEP_USE for each row
 declare wire clob;command_value varchar2(80);state_value varchar2(30);d json_object_t;
begin
 if not inserting then raise_application_error(-20886,'ASSEMBLY_STEP_USE_IMMUTABLE');end if;
 if RRL_ASSEMBLY_SCALE_API.write_allowed('USE')!=1 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=:new.STOCK_OPERATION_ID then
  raise_application_error(-20882,'ASSEMBLY_CANONICAL_STOCK_TRANSACTION_REQUIRED');end if;
 select CANONICAL_REQUEST,COMMAND_TYPE,STATE into wire,command_value,state_value from RRL_STOCK_OPERATION where OPERATION_ID=:new.STOCK_OPERATION_ID;
 d:=json_object_t.parse(wire);
 if command_value!='CASE_PICK_CONFIRM'or state_value!='IN_FLIGHT'or d.get_string('actor')is null or d.get_string('actor')!=:new.OPERATOR_ID
  or d.get_object('metadata').get_string('assembly_step_id')is null or d.get_object('metadata').get_string('assembly_step_id')!=:new.STEP_ID then
  raise_application_error(-20882,'ASSEMBLY_STEP_USE_ROOT_REQUIRED');end if;
end;
/
