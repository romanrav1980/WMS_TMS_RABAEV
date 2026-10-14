declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_SBORKA_PALLETS' and COLUMN_NAME='SCAN_CONTENT_SIGNATURE';
 if n=0 then execute immediate 'alter table RRL_SBORKA_PALLETS add(SCAN_CONTENT_SIGNATURE varchar2(64),SCAN_QC_OPERATION_ID varchar2(100),WEIGHT_CONTENT_SIGNATURE varchar2(64),WEIGHT_QC_OPERATION_ID varchar2(100),WEIGHT_QC_METHOD varchar2(20),WEIGHT_QC_EXPECTED number,WEIGHT_QC_TOLERANCE number)';end if;
end;
/
create or replace trigger RRL_QC_STAMP_GUARD
 before insert or update of SCAN_CONTENT_SIGNATURE,SCAN_QC_OPERATION_ID,WEIGHT_CONTENT_SIGNATURE,WEIGHT_QC_OPERATION_ID,WEIGHT_QC_METHOD,WEIGHT_QC_EXPECTED,WEIGHT_QC_TOLERANCE on RRL_SBORKA_PALLETS
 for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 -- Clearing an approval is safe and is also used by the existing document edits.
 if :new.SCAN_CONTENT_SIGNATURE is null and :new.WEIGHT_CONTENT_SIGNATURE is null then return;end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'QUALITY_APPROVAL_ROOT_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind!='OUTGOING_PALLET_CHECK' then raise_application_error(-20863,'QUALITY_APPROVAL_COMMAND_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(:new.ID)));
end;
/
create or replace trigger RRL_QC_ROWS_INVALIDATE
 after update of ARTICUL,QUANTITY,EI,PALLET_UID or delete on RRL_SBORKA_PALLET_ROWS
 for each row
begin
 if deleting or nvl(:new.ARTICUL,chr(0))!=nvl(:old.ARTICUL,chr(0))
  or nvl(:new.QUANTITY,-1)!=nvl(:old.QUANTITY,-1) or nvl(:new.EI,chr(0))!=nvl(:old.EI,chr(0))
  or nvl(:new.PALLET_UID,chr(0))!=nvl(:old.PALLET_UID,chr(0)) then
  update RRL_SBORKA_PALLETS set SCAN_CONTENT_SIGNATURE=null,WEIGHT_CONTENT_SIGNATURE=null where PALLET_UID=:old.PALLET_UID;
  if not deleting and nvl(:new.PALLET_UID,chr(0))!=nvl(:old.PALLET_UID,chr(0)) then
   update RRL_SBORKA_PALLETS set SCAN_CONTENT_SIGNATURE=null,WEIGHT_CONTENT_SIGNATURE=null where PALLET_UID=:new.PALLET_UID;
  end if;
 end if;
end;
/
create or replace trigger RRL_QC_ROWS_INSERT
 after insert on RRL_SBORKA_PALLET_ROWS for each row
begin
 update RRL_SBORKA_PALLETS set SCAN_CONTENT_SIGNATURE=null,WEIGHT_CONTENT_SIGNATURE=null where PALLET_UID=:new.PALLET_UID;
end;
/