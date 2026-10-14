create or replace trigger RRL_HU_CONTAINER_GUARD before insert or update of HU_KIND,HU_TYPE,HU_CONTENT_VERSION,HU_CURRENT_CELL,HU_TARE_WEIGHT_KG on RRL_PALLETS for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 if inserting and :new.HU_KIND='STOCK' then return;end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
  sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_METADATA_ROOT_COMMAND_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind not in('HU_CREATE','HU_ATTACH','HU_DETACH','HU_REPACK','HU_MOVE','HU_TASK_COMPLETE','HU_SHIP','HU_UNPACK','HU_RELOCATE_SLOT') then raise_application_error(-20863,'HU_METADATA_COMMAND_INVALID');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
 if updating and (:new.HU_KIND!=:old.HU_KIND or :new.HU_CONTENT_VERSION!=:old.HU_CONTENT_VERSION+1) then raise_application_error(-20863,'HU_IDENTITY_OR_VERSION_INVALID');end if;
end;
/
