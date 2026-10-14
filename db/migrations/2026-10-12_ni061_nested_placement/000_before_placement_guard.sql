create or replace trigger RRL_INTERWARE_PLACEMENT_GUARD before insert or update or delete on RRL_INTERWARE_PLACEMENT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_PLACEMENT_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_PLACEMENT_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='TASK_COMPLETE'and STATE='IN_FLIGHT'and json_value(CANONICAL_REQUEST,'$.source.task_id' returning number)=:new.TASK_ID and ACTOR=:new.ACTOR;
 if n!=1 then raise_application_error(-20863,'INTERWARE_PLACEMENT_TASK_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_PUT_PLAN p join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=p.RECEIPT_OPERATION_ID where p.TASK_ID=:new.TASK_ID and r.OPERATION_ID=:new.RECEIPT_OPERATION_ID and p.TARGET_CELL=:new.TARGET_CELL and r.ROOT_UID=:new.ROOT_UID and r.WARE_ID=:new.WARE_ID and r.BASE_QTY=:new.BASE_QTY and r.BASE_UOM=:new.BASE_UOM;
 if n!=1 then raise_application_error(-20863,'INTERWARE_PLACEMENT_ORIGINAL_RECEIPT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_PLACEMENT',to_char(:new.TASK_ID,'TM9')));
end;

/
