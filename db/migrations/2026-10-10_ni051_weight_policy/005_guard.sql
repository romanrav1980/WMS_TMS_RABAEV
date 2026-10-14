create or replace trigger RRL_QC_MASS_POLICY_GUARD
 before insert or delete or update of QC_BASE_WEIGHT_KG,QC_BOX_WEIGHT_KG,QC_WEIGHT_BASE_UOM,QC_WEIGHT_VERSION on RRL_RECEIPT_SKU_RULE
 for each row
begin
 if inserting and :new.QC_BASE_WEIGHT_KG is null and :new.QC_BOX_WEIGHT_KG is null and :new.QC_WEIGHT_BASE_UOM is null and :new.QC_WEIGHT_VERSION=0 then return;end if;
 if deleting and :old.QC_BASE_WEIGHT_KG is null and :old.QC_BOX_WEIGHT_KG is null and :old.QC_WEIGHT_BASE_UOM is null and :old.QC_WEIGHT_VERSION=0 then return;end if;
 if nvl(sys_context('RRL_STOCK_WRITE_CTX','MODE'),chr(0))!='CONFIG'
  or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION') not in('warehouse_settings_edit','finished_goods_edit')
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
  raise_application_error(-20863,'QUALITY_MASS_CONFIGURATION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if updating and :new.QC_WEIGHT_VERSION!=:old.QC_WEIGHT_VERSION+1 then raise_application_error(-20863,'QUALITY_MASS_VERSION_INCREMENT_REQUIRED');end if;
 if not deleting and ((:new.QC_BASE_WEIGHT_KG is null and :new.QC_BOX_WEIGHT_KG is not null)
  or(:new.QC_BASE_WEIGHT_KG is not null and :new.QC_BOX_WEIGHT_KG is null)
  or(:new.QC_BASE_WEIGHT_KG is not null and :new.QC_WEIGHT_BASE_UOM is null)) then
  raise_application_error(-20863,'QUALITY_MASS_COMPLETE_POLICY_REQUIRED');end if;
end;
/