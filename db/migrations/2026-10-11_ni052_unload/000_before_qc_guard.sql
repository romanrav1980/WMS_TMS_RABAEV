create or replace trigger RRL_QC_STAMP_GUARD
 before insert or update of SCAN_CONTENT_SIGNATURE,SCAN_QC_OPERATION_ID,WEIGHT_CONTENT_SIGNATURE,WEIGHT_QC_OPERATION_ID,WEIGHT_QC_METHOD,WEIGHT_QC_EXPECTED,WEIGHT_QC_TOLERANCE,SCAN_MARK_PROVED,SCAN_PHYSICAL_UNIT_COUNT,SCAN_ITEM_PROVED on RRL_SBORKA_PALLETS
 for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 -- Clearing an approval is safe and is also used by the existing document edits.
 if :new.SCAN_CONTENT_SIGNATURE is null and :new.WEIGHT_CONTENT_SIGNATURE is null and :new.SCAN_MARK_PROVED=0 and :new.SCAN_PHYSICAL_UNIT_COUNT=0 and :new.SCAN_ITEM_PROVED=0 then return;end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'QUALITY_APPROVAL_ROOT_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind!='OUTGOING_PALLET_CHECK' then raise_application_error(-20863,'QUALITY_APPROVAL_COMMAND_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(:new.ID)));
end;
/
