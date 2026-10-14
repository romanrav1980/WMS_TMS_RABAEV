create or replace trigger RRL_WEIGHT_CHOICE_GUARD before insert or update or delete on RRL_PICK_WEIGHT_CHOICE for each row
begin
 if deleting then raise_application_error(-20863,'WEIGHT_CHOICE_RETAIN_ORIGINAL_HISTORY');end if;
 if sys_context('RRL_WEIGHT_CHOICE_CTX','TX_ID')is null
  or sys_context('RRL_WEIGHT_CHOICE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_WEIGHT_CHOICE_CTX','CHOICE_ID')is null
  or sys_context('RRL_WEIGHT_CHOICE_CTX','CHOICE_ID')!=:new.CHOICE_ID
  then raise_application_error(-20863,'WEIGHT_CHOICE_TRUSTED_PACKAGE_REQUIRED');end if;
 if inserting then
  if sys_context('RRL_WEIGHT_CHOICE_CTX','PHASE')is null or sys_context('RRL_WEIGHT_CHOICE_CTX','PHASE')!='APPROVE'
   or :new.STATUS!='ACCEPTED'or :new.APPROVED_BY!=sys_context('RRL_WEIGHT_CHOICE_CTX','ACTOR')
   or :new.PICK_PLAN_ID is not null or :new.PICK_PLAN_LINE_ID is not null or :new.USED_AT is not null
   or :new.CANCELLED_BY is not null or :new.CANCELLED_AT is not null or :new.CANCEL_REASON is not null
   then raise_application_error(-20863,'WEIGHT_CHOICE_APPROVAL_INITIAL_STATE_REQUIRED');end if;
 else
  if :new.CHOICE_ID!=:old.CHOICE_ID or :new.CUSTOMER_ORDER_ROW_ID!=:old.CUSTOMER_ORDER_ROW_ID
   or :new.CUSTOMER_ORDER_ID!=:old.CUSTOMER_ORDER_ID or :new.WARE_ID!=:old.WARE_ID or :new.ARTICLE!=:old.ARTICLE
   or :new.PHYSICAL_UNIT_KEY!=:old.PHYSICAL_UNIT_KEY or :new.SOURCE_UID!=:old.SOURCE_UID or :new.SOURCE_CELL!=:old.SOURCE_CELL
   or :new.STOCK_VERSION!=:old.STOCK_VERSION or :new.NET_WEIGHT_KG!=:old.NET_WEIGHT_KG or :new.POLICY_VERSION!=:old.POLICY_VERSION
   or :new.TOLERANCE_PCT!=:old.TOLERANCE_PCT or :new.ORIGINAL_ORDER_KG!=:old.ORIGINAL_ORDER_KG
   or :new.ORIGINAL_REMAINING_KG!=:old.ORIGINAL_REMAINING_KG or :new.CHOICE_MODE!=:old.CHOICE_MODE
   or :new.APPROVED_BY!=:old.APPROVED_BY or :new.APPROVED_AT!=:old.APPROVED_AT or :new.REASON_TEXT!=:old.REASON_TEXT
   or :new.SOURCE_SIGNATURE!=:old.SOURCE_SIGNATURE
   or dbms_lob.compare(:new.SOURCE_JSON,:old.SOURCE_JSON)!=0 or dbms_lob.compare(:new.REQUEST_JSON,:old.REQUEST_JSON)!=0
   or dbms_lob.compare(:new.RESULT_JSON,:old.RESULT_JSON)!=0
   then raise_application_error(-20863,'WEIGHT_CHOICE_ORIGINAL_IMMUTABLE');end if;
  if sys_context('RRL_WEIGHT_CHOICE_CTX','PHASE')is null or sys_context('RRL_WEIGHT_CHOICE_CTX','PHASE')!='CANCEL'
   or :old.STATUS!='ACCEPTED'or :new.STATUS!='CANCELLED'
   or :new.CANCELLED_BY is null or :new.CANCELLED_BY!=sys_context('RRL_WEIGHT_CHOICE_CTX','ACTOR')
   or :new.CANCELLED_AT is null or :new.CANCEL_REASON is null
   or :new.PICK_PLAN_ID is not null or :new.PICK_PLAN_LINE_ID is not null or :new.USED_AT is not null
   then raise_application_error(-20863,'WEIGHT_CHOICE_VALID_CANCELLATION_REQUIRED');end if;
 end if;
end;
/
