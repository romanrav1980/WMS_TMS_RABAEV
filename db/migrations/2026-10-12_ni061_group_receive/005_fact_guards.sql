create or replace package RRL_IW_GROUP_FACT_GUARD authid definer as
 procedure assert_head(p_operation varchar2,p_plan varchar2,p_uid varchar2,p_ware number,p_actor varchar2,p_kind varchar2,p_cell varchar2 default null,p_unload varchar2 default null);
end;
/
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
create or replace trigger RRL_IW_GROUP_UNLOAD_GUARD before insert or update or delete on RRL_IW_GROUP_UNLOAD for each row
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_UNLOAD_IMMUTABLE');end if;
 RRL_IW_GROUP_FACT_GUARD.assert_head(:new.OPERATION_ID,:new.PLAN_OPERATION_ID,:new.ROOT_UID,:new.WARE_ID,:new.ACTOR,'INTERWARE_UNLOAD');
end;
/
create or replace trigger RRL_IW_GROUP_RECEIPT_GUARD before insert or update or delete on RRL_IW_GROUP_RECEIPT for each row
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_RECEIPT_IMMUTABLE');end if;
 RRL_IW_GROUP_FACT_GUARD.assert_head(:new.OPERATION_ID,:new.PLAN_OPERATION_ID,:new.ROOT_UID,:new.WARE_ID,:new.ACTOR,'INTERWARE_RECEIVE',:new.RECEIVE_CELL,:new.UNLOAD_OPERATION_ID);
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_GROUP_UNLOAD',:new.UNLOAD_OPERATION_ID));
end;
/
create or replace trigger RRL_IW_GROUP_REC_LINE_GUARD before insert or update or delete on RRL_IW_GROUP_RECEIPT_LINE for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;wire clob;kind_value varchar2(80);state_value varchar2(20);cell_value varchar2(60);
begin
 if not inserting or op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_GROUP_LINE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_value,state_value,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
 cell_value:=json_object_t.parse(wire).get_object('domain').get_string('receive_cell');
 select count(*)into n from json_table(wire,'$.domain.lots[*]'columns(U varchar2(200)path '$.uid',ST_ID number path '$.st_id',ARTICLE_VALUE varchar2(160)path '$.article',QTY_VALUE varchar2(60)path '$.quantity',UOM_VALUE varchar2(20)path '$.base_uom'))j
 where U=:new.ROOT_UID and ST_ID=:new.ST_ID and ARTICLE_VALUE=:new.ARTICLE and RRL_STOCK_MATH.quantity(QTY_VALUE)=:new.BASE_QTY and UOM_VALUE=:new.BASE_UOM;
 if kind_value!='INTERWARE_RECEIVE'or state_value!='IN_FLIGHT'or n!=1 then raise_application_error(-20863,'INTERWARE_GROUP_LINE_RESOLVED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_EVENTS where ID_EVENT=:new.STOCK_EVENT_ID and OPERATION_ID=op and UID_POLETA=:new.ROOT_UID and BASE_QTY=:new.BASE_QTY and BASE_UOM=:new.BASE_UOM and CELL_TO=cell_value;
 if n!=1 then raise_application_error(-20863,'INTERWARE_GROUP_LINE_EXACT_EVENT_REQUIRED');end if;
end;
/
