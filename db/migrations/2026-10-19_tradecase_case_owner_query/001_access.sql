create or replace package body RRL_TRADE_CASE_ACCESS as
 procedure assert_scope(p_task number,p_actor varchar2,p_write number)is ware number;total number;tagged number;n number;found_owner number;
 begin
  if RRL_ACCESS_API.is_admin(p_actor)=1 then return;end if;
  select WARE_ID into ware from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  select count(*)into n from RRL_TRADE_SITE where WARE_ID=ware;
  select count(*),count(t.CUSTOMER_ORDER_ROW_ID)into total,tagged from RRL_CASE_PICK_LINE l
   left join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=l.PICK_PLAN_LINE_ID
   left join RRL_TRADE_ORDER_LINE t on t.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID where l.CASE_PICK_TASK_ID=p_task;
  if n=0 and tagged=0 then return;end if;
  if total=0 or tagged<>total then raise_application_error(-20886,'TRADE_CASE_ORDER_BINDING_REQUIRED');end if;
  for line in(select l.CASE_PICK_LINE_ID,l.PICK_TASK_ID,t.SOURCE_OWNER_ID from RRL_CASE_PICK_LINE l
   join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=l.PICK_PLAN_LINE_ID
   join RRL_TRADE_ORDER_LINE t on t.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID where l.CASE_PICK_TASK_ID=p_task)loop
   found_owner:=0;
   for owner in(select distinct a.OWNER_ID from(
    select u.PHYSICAL_UNIT_KEY from RRL_CASE_CARRIER_LOT h join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=h.LOT_UID
     where h.CASE_PICK_LINE_ID=line.CASE_PICK_LINE_ID
    union
    select h.PHYSICAL_UNIT_KEY from RRL_TRADE_CASE_RETURN_UNIT h join RRL_STOCK_OPERATION op on op.OPERATION_ID=h.RETURN_OPERATION and op.STATE='APPLIED'
     where h.CASE_PICK_TASK_ID=p_task
    union
    select u.PHYSICAL_UNIT_KEY from RRL_STOCK_RESERVATION r join RRL_WMS_RECEIPT_UNIT u on u.HARD_RESERVATION_ID=r.RESERVATION_ID
     where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_LINE_ID=line.PICK_TASK_ID and r.RESERVATION_KIND='HARD'and r.STATUS in('ACTIVE','ALLOCATED','PICKING')
   ) selected_units join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=selected_units.PHYSICAL_UNIT_KEY)loop
    found_owner:=1;RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,owner.OWNER_ID,p_write);
   end loop;
   if found_owner=0 then RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,line.SOURCE_OWNER_ID,p_write);end if;
  end loop;
 end;
 function execution_allowed(p_task number,p_actor varchar2)return number is t RRL_CASE_PICK_TASK%rowtype;total number;tagged number;n number;
 begin
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if t.WARE_ID is null or t.CONTENT_VERSION is null or t.SHIPPED_OPERATION is not null then return 0;end if;
  select count(*)into n from RRL_TRADE_SITE where WARE_ID=t.WARE_ID;if n<>1 then return 0;end if;
  select count(*)into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=p_task and ACTIVE_FLAG=1;if n<>0 then return 0;end if;
  select count(*)into n from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=p_task and STATE in('OPEN','BLOCKED','HOLD');if n<>0 then return 0;end if;
  select count(*),count(ol.CUSTOMER_ORDER_ROW_ID)into total,tagged from RRL_CASE_PICK_LINE cl join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=cl.PICK_PLAN_LINE_ID
   left join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID where cl.CASE_PICK_TASK_ID=p_task;
  if total=0 or tagged<>total then return 0;end if;
  select count(*)into n from RRL_CASE_PICK_LINE cl where cl.CASE_PICK_TASK_ID=p_task and(
   not exists(select 1 from RRL_ARTICULS a where a.ACTICUL=cl.ARTICUL and nvl(a.TYPE_W,0)not in(2,3,5,6,7))
   or not exists(select 1 from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=cl.ARTICUL and u.INPUT_UOM='EA'and u.BASE_UOM='EA'and u.NUMERATOR=1 and u.DENOMINATOR=1
    and u.POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION where ARTICUL=cl.ARTICUL and INPUT_UOM='EA'))
   or not exists(select 1 from RRL_SKU_RECEIPT_POLICY x where x.ARTICUL=cl.ARTICUL and x.MARKING_REQUIRED=1 and nvl(x.SERIALIZED_WEIGHT_BOXES,0)=0)
   or not exists(select 1 from RRL_SKU_RECEIPT_PROFILE x where x.ARTICUL=cl.ARTICUL and x.SYSTEM_CODE='CRPT'and x.PROFILE_CODE='TOBACCO'and x.SCAN_MODE='UNIT')
   or exists(select 1 from RRL_SKU_RECEIPT_PROFILE x where x.ARTICUL=cl.ARTICUL and(x.SYSTEM_CODE<>'CRPT'or x.PROFILE_CODE<>'TOBACCO'or x.SCAN_MODE<>'UNIT')));
  if n<>0 then return 0;end if;
  assert_scope(p_task,p_actor,1);return 1;
 exception when no_data_found then return 0;when others then if sqlcode in(-20882,-20886)then return 0;end if;raise;
 end;
 function allowed(p_task number,p_actor varchar2)return number is
 begin
  assert_scope(p_task,p_actor,0);return 1;
 exception when others then
  if sqlcode in(-20882,-20886,-1403)then return 0;end if;raise;
 end;
end;


/
