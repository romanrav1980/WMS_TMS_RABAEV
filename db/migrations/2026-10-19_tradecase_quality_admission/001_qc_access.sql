create or replace package body RRL_OUTGOING_QC_ACCESS as
 procedure assert_identifier(p_identifier varchar2,p_actor varchar2)is ware number;user_ware number;grp varchar2(100);legacy_ok number:=0;
 begin
  select WARE_ID into ware from RRL_SBORKA_PALLETS where PALLET_UID=p_identifier;
  select WARE_ID,USER_GROUP into user_ware,grp from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if(RRL_HAS_WRIGHT(p_actor,'outgoing_pallet_check')=1 or RRL_HAS_WRIGHT(p_actor,'stock_posting_shipping')=1 or RRL_HAS_WRIGHT(p_actor,'CLOSE_OTHOD_NAKLAD')=1)
   and(upper(trim(grp))='GLOBAL_ADMIN'or user_ware=ware)then legacy_ok:=1;end if;
  if ware is null or(legacy_ok<>1 and RRL_ACCESS_API.allowed(p_actor,'outgoing_pallet_check','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(ware))<>1)then raise_application_error(-20882,'OUTGOING_QC_CURRENT_WARE_REQUIRED');end if;
  for ct in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS sp on sp.ID=c.LEGACY_SBORKA_PALLET_ID where sp.PALLET_UID=p_identifier)loop
   RRL_TRADE_CASE_ACCESS.assert_scope(ct.CASE_PICK_TASK_ID,p_actor,1);
  end loop;
  for o in(select distinct a.OWNER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=f.PICKED_PALLET_UID
   join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where f.PALLET_UID=p_identifier)loop RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,o.OWNER_ID,1);end loop;
 exception when no_data_found then raise_application_error(-20882,'OUTGOING_QC_CURRENT_SOURCE_AND_ACTOR_REQUIRED');
 end;
end;
/
