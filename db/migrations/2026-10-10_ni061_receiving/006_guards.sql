create or replace trigger RRL_INTERWARE_UNLOAD_GUARD before insert or update or delete on RRL_INTERWARE_UNLOAD for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');k varchar2(80);st varchar2(20);resolved clob;d json_object_t;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_UNLOAD_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_UNLOAD_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into k,st,resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;d:=json_object_t.parse(resolved).get_object('domain');
 if k!='INTERWARE_UNLOAD' or st!='IN_FLIGHT' or d.get_string('plan_operation_id')!=:new.PLAN_OPERATION_ID or d.get_string('uid')!=:new.ROOT_UID or d.get_number('warehouse_id')!=:new.WARE_ID or d.get_string('vehicle_number')!=:new.VEHICLE_NUMBER or d.get_string('inbound_dock')!=:new.INBOUND_DOCK or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'INTERWARE_UNLOAD_RESOLVED_SOURCE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_PLAN',:new.PLAN_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_UNLOAD',op));
end;
/
create or replace trigger RRL_INTERWARE_RECEIPT_GUARD before insert or update or delete on RRL_INTERWARE_RECEIPT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');k varchar2(80);st varchar2(20);resolved clob;d json_object_t;n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_RECEIPT_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_RECEIPT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into k,st,resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;d:=json_object_t.parse(resolved).get_object('domain');
 if k!='INTERWARE_RECEIVE' or st!='IN_FLIGHT' or d.get_string('plan_operation_id')!=:new.PLAN_OPERATION_ID or d.get_string('uid')!=:new.ROOT_UID or d.get_number('warehouse_id')!=:new.WARE_ID or d.get_string('receive_cell')!=:new.RECEIVE_CELL or d.get_string('article')!=:new.ARTICLE or RRL_STOCK_MATH.quantity(d.get_string('quantity'))!=:new.BASE_QTY or d.get_string('base_uom')!=:new.BASE_UOM or d.get_string('source_load_operation_id')!=:new.SOURCE_LOAD_OPERATION_ID or d.get_string('unload_operation_id')!=:new.UNLOAD_OPERATION_ID or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'INTERWARE_RECEIPT_RESOLVED_SOURCE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_PLAN',:new.PLAN_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_UNLOAD',:new.UNLOAD_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_RECEIPT',op));
 select count(*)into n from RRL_EVENTS where ID_EVENT=:new.STOCK_EVENT_ID and OPERATION_ID=op and UID_POLETA=:new.ROOT_UID and BASE_QTY=:new.BASE_QTY and BASE_UOM=:new.BASE_UOM and CELL_TO=:new.RECEIVE_CELL;
 if n!=1 then raise_application_error(-20863,'INTERWARE_RECEIPT_STOCK_EVENT_REQUIRED');end if;
end;
/
