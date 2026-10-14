create or replace trigger RRL_HU_CLAIM_MEASURE_GUARD before insert or update of HU_GROSS_WEIGHT_KG,HU_BOUNDING_VOLUME_M3,HU_COMPOSITION_VERSION on RRL_RECEIPT_SLOT_CLAIM for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind varchar2(80);version_no number;begin
 if inserting and :new.HU_GROSS_WEIGHT_KG is null and :new.HU_BOUNDING_VOLUME_M3 is null and :new.HU_COMPOSITION_VERSION is null then return;end if;
 if updating then raise_application_error(-20863,'HU_CLAIM_MEASURE_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or :new.HU_GROSS_WEIGHT_KG is null or :new.HU_BOUNDING_VOLUME_M3 is null or least(:new.HU_GROSS_WEIGHT_KG,:new.HU_BOUNDING_VOLUME_M3)<=0 then raise_application_error(-20863,'HU_CLAIM_MEASURE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE into kind from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind!='HU_TASK_COMPLETE' then raise_application_error(-20863,'HU_CLAIM_MEASURE_TASK_REQUIRED');end if;
 select HU_CONTENT_VERSION into version_no from RRL_PALLETS where UID_PALLET=:new.UID_PALLET and HU_KIND='CONTAINER';
 if :new.HU_COMPOSITION_VERSION is null or :new.HU_COMPOSITION_VERSION!=version_no then raise_application_error(-20863,'HU_CLAIM_MEASURE_VERSION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
end;
/
