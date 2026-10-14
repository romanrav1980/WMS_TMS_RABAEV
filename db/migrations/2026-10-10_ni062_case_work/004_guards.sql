create or replace trigger RRL_STORE_CASE_APPEND_GUARD before insert or update or delete on RRL_STORE_DISCREPANCY_CASE for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);v_action varchar2(30);
begin
 if deleting then raise_application_error(-20863,'STORE_CASE_HISTORY_REQUIRED');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_CASE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,json_value(RESOLVED_PLAN_JSON,'$.domain.action') into v_kind,v_state,v_action from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_state!='IN_FLIGHT' then raise_application_error(-20863,'STORE_CASE_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_DISCREPANCY_CASE',:new.CASE_ID));
 if inserting then
  if v_kind!='STORE_RECEIPT' or op!=:new.CASE_ID or :new.STATUS!='OPEN' or :new.CASE_VERSION!=1 or :new.EXPEDITION_USER is not null or :new.SECURITY_USER is not null or :new.SEARCH_DEADLINE is not null then raise_application_error(-20863,'STORE_CASE_RECEIPT_ROOT_REQUIRED');end if;
 else
  if v_kind!='STORE_CASE_WORK' or :new.CASE_VERSION!=:old.CASE_VERSION+1 or :new.LAST_DECISION_OPERATION is null or :new.LAST_DECISION_OPERATION!=op then raise_application_error(-20863,'STORE_CASE_EXPLICIT_VERSIONED_ACTION_REQUIRED');end if;
  if :new.CASE_ID!=:old.CASE_ID or :new.LOAD_OPERATION_ID!=:old.LOAD_OPERATION_ID or :new.STORE_ADDR!=:old.STORE_ADDR
   or :new.REASON_TEXT!=:old.REASON_TEXT or :new.REPORTED_BY!=:old.REPORTED_BY or :new.CREATED_AT!=:old.CREATED_AT then raise_application_error(-20863,'STORE_CASE_ORIGINAL_SOURCE_IMMUTABLE');end if;
  if v_action='ASSIGN' then
   if :new.STATUS!='ASSIGNED' or :new.EXPEDITION_USER is null or :new.SECURITY_USER is null or :new.EXPEDITION_USER=:new.SECURITY_USER or :new.SEARCH_DEADLINE is null or :new.ASSIGNED_TO!=:new.EXPEDITION_USER then raise_application_error(-20863,'STORE_CASE_EXPLICIT_ASSIGNMENT_REQUIRED');end if;
  elsif :new.STATUS!=:old.STATUS or nvl(:new.EXPEDITION_USER,'#NULL#')!=nvl(:old.EXPEDITION_USER,'#NULL#')
   or nvl(:new.SECURITY_USER,'#NULL#')!=nvl(:old.SECURITY_USER,'#NULL#') or nvl(:new.ASSIGNED_TO,'#NULL#')!=nvl(:old.ASSIGNED_TO,'#NULL#')
   or(:new.SEARCH_DEADLINE is null and :old.SEARCH_DEADLINE is not null) or(:new.SEARCH_DEADLINE is not null and :old.SEARCH_DEADLINE is null)
   or :new.SEARCH_DEADLINE!=:old.SEARCH_DEADLINE then raise_application_error(-20863,'STORE_CASE_ASSIGNMENT_IMMUTABLE_FOR_REPORT_OR_LOSS');end if;
 end if;
end;
/
create or replace trigger RRL_STORE_OBLIGATION_GUARD before insert or update or delete on RRL_STORE_DELIVERY_OBLIGATION for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);v_action varchar2(30);v_case varchar2(100);v_line number;
begin
 if deleting then raise_application_error(-20863,'STORE_OBLIGATION_HISTORY_REQUIRED');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_OBLIGATION_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,json_value(RESOLVED_PLAN_JSON,'$.domain.action'),json_value(RESOLVED_PLAN_JSON,'$.domain.case_id'),json_value(RESOLVED_PLAN_JSON,'$.domain.line_no' returning number)
 into v_kind,v_state,v_action,v_case,v_line from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_state!='IN_FLIGHT' then raise_application_error(-20863,'STORE_OBLIGATION_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_DELIVERY_OBLIGATION',:new.CASE_ID||':'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.LINE_NO)||':'||:new.KIND));
 if inserting then
  if v_kind!='STORE_RECEIPT' or op!=:new.CASE_ID or :new.STATUS!='OPEN' then raise_application_error(-20863,'STORE_OBLIGATION_RECEIPT_ROOT_REQUIRED');end if;
 else
  if v_kind!='STORE_CASE_WORK' or v_action!='LOSS_CONFIRM' or v_case!=:new.CASE_ID or v_line!=:new.LINE_NO or :new.KIND!='MISSING_INVESTIGATION'
   or :old.STATUS not in('OPEN','SEARCHING') or :new.STATUS!='LOSS_CONFIRMED' then raise_application_error(-20863,'STORE_OBLIGATION_EXPLICIT_LOSS_DECISION_REQUIRED');end if;
  if :new.CASE_ID!=:old.CASE_ID or :new.LINE_NO!=:old.LINE_NO or :new.KIND!=:old.KIND or :new.BASE_QTY!=:old.BASE_QTY or :new.BASE_UOM!=:old.BASE_UOM then raise_application_error(-20863,'STORE_OBLIGATION_ORIGINAL_QUANTITY_IMMUTABLE');end if;
 end if;
end;
/
