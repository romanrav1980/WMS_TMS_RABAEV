create or replace trigger RRL_QC_WARE_POLICY_GUARD
 before insert or delete or update of OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT on RRL_RECEIPT_WARE_SETTINGS for each row
begin
 if inserting and :new.OUTGOING_QC_MODE is null and :new.OUTGOING_QC_INDEPENDENT=0 then return;end if;
 if nvl(sys_context('RRL_STOCK_WRITE_CTX','MODE'),chr(0))!='CONFIG' or nvl(sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION'),chr(0))!='warehouse_settings_edit'
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'QUALITY_WAREHOUSE_CONFIGURATION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
end;
/