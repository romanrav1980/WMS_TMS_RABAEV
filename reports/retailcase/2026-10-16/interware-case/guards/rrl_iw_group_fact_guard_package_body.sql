create or replace package body RRL_IW_GROUP_FACT_GUARD as
 procedure assert_head(p_operation varchar2,p_plan varchar2,p_uid varchar2,p_ware number,p_actor varchar2,p_kind varchar2,p_cell varchar2 default null,p_unload varchar2 default null)is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_value varchar2(80);state_value varchar2(20);wire clob;d json_object_t;
 begin
 if op is null or op!=p_operation or p_actor!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_GROUP_FACT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_value,state_value,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;d:=json_object_t.parse(wire).get_object('domain');
 if kind_value!=p_kind or state_value!='IN_FLIGHT'or not d.get_boolean('group_receipt')or d.get_string('plan_operation_id')!=p_plan or d.get_string('uid')!=p_uid or d.get_number('warehouse_id')!=p_ware then raise_application_error(-20863,'INTERWARE_GROUP_EXACT_FACT_REQUIRED');end if;
 if p_kind='INTERWARE_RECEIVE'and(d.get_string('receive_cell')!=p_cell or d.get_string('unload_operation_id')!=p_unload)then raise_application_error(-20863,'INTERWARE_GROUP_EXACT_RECEIPT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_GROUP_PLAN',p_plan));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW',case when p_kind='INTERWARE_RECEIVE'then 'RRL_IW_GROUP_RECEIPT'else 'RRL_IW_GROUP_UNLOAD'end,op));
 end;
end;
/
