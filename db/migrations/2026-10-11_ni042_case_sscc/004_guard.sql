create or replace trigger RRL_CASE_SSCC_LABEL_GUARD before insert or update or delete on RRL_CASE_SSCC_LABEL for each row
begin
 if deleting then raise_application_error(-20863,'CASE_SSCC_HISTORY_IMMUTABLE');end if;
 if sys_context('RRL_CASE_SSCC_CTX','TX_ID')is null or sys_context('RRL_CASE_SSCC_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_CASE_SSCC_CTX','ACTOR')is null then raise_application_error(-20863,'CASE_SSCC_TRUSTED_OWNER_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if inserting then
  if :new.CREATED_BY!=sys_context('RRL_CASE_SSCC_CTX','ACTOR')or :new.CONFIRMED_AT is not null then raise_application_error(-20863,'CASE_SSCC_INVALID_BIRTH');end if;
 elsif :new.OPERATION_ID!=:old.OPERATION_ID or :new.CASE_PICK_TASK_ID!=:old.CASE_PICK_TASK_ID or :new.SSCC!=:old.SSCC
  or :new.ORIGINAL_CARRIER!=:old.ORIGINAL_CARRIER or :new.WARE_ID!=:old.WARE_ID or :new.PALLET_TYPE_ID!=:old.PALLET_TYPE_ID
  or :new.REQUESTED_VERSION!=:old.REQUESTED_VERSION or :new.CREATED_BY!=:old.CREATED_BY or :new.CREATED_AT!=:old.CREATED_AT
  or dbms_lob.compare(:new.REQUEST_JSON,:old.REQUEST_JSON)!=0 or dbms_lob.compare(:new.RESULT_JSON,:old.RESULT_JSON)!=0
  or :old.CONFIRMED_AT is not null or :new.CONFIRMED_AT is null or :new.CONFIRMED_BY!=sys_context('RRL_CASE_SSCC_CTX','ACTOR')
 then raise_application_error(-20863,'CASE_SSCC_HISTORY_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_CASE_SSCC_ID_GUARD before update of SSCC on RRL_CASE_PICK_TASK for each row
declare n number;
begin
 if :new.SSCC=:old.SSCC then return;end if;
 select count(*)into n from RRL_CASE_SSCC_LABEL where CASE_PICK_TASK_ID=:old.CASE_PICK_TASK_ID;
 if n>0 and(sys_context('RRL_CASE_SSCC_CTX','TX_ID')is null or sys_context('RRL_CASE_SSCC_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false))
 then raise_application_error(-20863,'CASE_SSCC_ID_IMMUTABLE');end if;
end;
/
