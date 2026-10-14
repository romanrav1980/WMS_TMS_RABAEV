CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_SAP_PALLET_WRITE_GUARD" 
before insert or delete or update of UID_PALLET,UNIT_COUNT,PRIHOD_NAKLAD_ID on RRL_PALLETS
for each row
declare n number;allowed_clone number:=0;op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
begin
 select count(*)into n from RRL_SAP_SUPPLY_ORDER
  where NAKLAD_ID=:new.PRIHOD_NAKLAD_ID or NAKLAD_ID=:old.PRIHOD_NAKLAD_ID;
 if n>0 and not RRL_SAP_RECEIPT_API.pallet_write_allowed then
  if inserting and op is not null and :new.CREATED_BY_STOCK_OP=op and :new.STOCK_ORIGIN_UID is not null
   and sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is not null
   and sys_context('RRL_STOCK_WRITE_CTX','TX_ID')=dbms_transaction.local_transaction_id(false)then
   select count(*)into allowed_clone from RRL_STOCK_OPERATION operation
    join json_table(operation.RESOLVED_PLAN_JSON,'$.domain.chunks[*]'columns(
      SOURCE_UID varchar2(150)path '$.source_uid',TARGET_UID varchar2(150)path '$.target_uid',
      QUANTITY_TEXT varchar2(60)path '$.quantity'))chunk on chunk.TARGET_UID=:new.UID_PALLET
    join RRL_SAP_PALLET_RECEIPT rec on rec.UID_PALLET=chunk.SOURCE_UID
    join RRL_SAP_SUPPLY_ORDER supply on supply.ORDER_ID=rec.ORDER_ID
    where operation.OPERATION_ID=op and operation.STATE='IN_FLIGHT'and operation.COMMAND_TYPE='CASE_PICK_CONFIRM'
     and chunk.SOURCE_UID=:new.STOCK_ORIGIN_UID and supply.NAKLAD_ID=:new.PRIHOD_NAKLAD_ID
     and chunk.QUANTITY_TEXT=RRL_STOCK_PLAN_HELPER.decimal_text(:new.UNIT_COUNT);
   if allowed_clone=0 then
    select count(*)into allowed_clone from RRL_STOCK_OPERATION operation
     join json_table(operation.RESOLVED_PLAN_JSON,'$.domain'columns(
       PARTIAL_FLAG varchar2(5)path '$.partial_receipt',SOURCE_UID varchar2(150)path '$.original_root_uid',TARGET_UID varchar2(150)path '$.uid',
       QUANTITY_TEXT varchar2(60)path '$.quantity',ORIGIN_UID varchar2(150)path '$.source_origin_uid',NAKLAD_ID number path '$.source_naklad_id'))d
      on d.TARGET_UID=:new.UID_PALLET
     where operation.OPERATION_ID=op and operation.STATE='IN_FLIGHT'and operation.COMMAND_TYPE='INTERWARE_RECEIVE'
      and d.PARTIAL_FLAG='true'and d.ORIGIN_UID=:new.STOCK_ORIGIN_UID
      and d.SOURCE_UID!=d.TARGET_UID and d.NAKLAD_ID=:new.PRIHOD_NAKLAD_ID
      and d.QUANTITY_TEXT=RRL_STOCK_PLAN_HELPER.decimal_text(:new.UNIT_COUNT);
   end if;
   if allowed_clone=1 then
    RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',:new.UID_PALLET));
    RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',:new.STOCK_ORIGIN_UID));
   end if;
  end if;
  if allowed_clone!=1 then raise_application_error(-20804,'SAP incoming pallets require the physical receiving API or planned native CASE split');end if;
 end if;
end;
/
