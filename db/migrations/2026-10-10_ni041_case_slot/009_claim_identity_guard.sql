-- Measured physical placement is immutable; changing its position uses explicit root delete+insert.
create or replace trigger RRL_HU_CLAIM_IDENTITY_GUARD before update or delete on RRL_RECEIPT_SLOT_CLAIM for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');state_name varchar2(20);
begin
 if :old.HU_GROSS_WEIGHT_KG is null and :old.HU_CASE_TASK_ID is null then return;end if;
 if updating then raise_application_error(-20863,'MEASURED_PLACEMENT_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'MEASURED_PLACEMENT_ROOT_RELEASE_REQUIRED');end if;
 select STATE into state_name from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if state_name!='IN_FLIGHT' then raise_application_error(-20863,'MEASURED_PLACEMENT_POSTING_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(:old.TASK_ID)));
 RRL_STOCK_LOCK_API.assert_held(40,RRL_STOCK_LOCK_API.resource_key('SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(:old.CELL_SLOT_ID)));
end;
/
