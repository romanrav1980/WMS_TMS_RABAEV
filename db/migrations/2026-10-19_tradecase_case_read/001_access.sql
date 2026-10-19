create or replace package RRL_TRADE_CASE_ACCESS authid defineras
 function allowed(p_task number,p_actor varchar2)return number;
 procedure assert_scope(p_task number,p_actor varchar2,p_write number);
end;

/
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
   for owner in(select distinct a.OWNER_ID from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
    where exists(select 1 from RRL_CASE_CARRIER_LOT h where h.CASE_PICK_LINE_ID=line.CASE_PICK_LINE_ID and h.LOT_UID=u.CURRENT_UID)
     or exists(select 1 from RRL_STOCK_RESERVATION r where r.RESERVATION_ID=u.HARD_RESERVATION_ID and r.SOURCE_DOC_TYPE='PICK_WAVE'
      and r.SOURCE_LINE_ID=line.PICK_TASK_ID and r.RESERVATION_KIND='HARD'and r.STATUS in('ACTIVE','ALLOCATED','PICKING')))loop
    found_owner:=1;RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,owner.OWNER_ID,p_write);
   end loop;
   if found_owner=0 then RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,line.SOURCE_OWNER_ID,p_write);end if;
  end loop;
 end;
 function allowed(p_task number,p_actor varchar2)return number is
 begin
  assert_scope(p_task,p_actor,0);return 1;
 exception when others then
  if sqlcode in(-20882,-20886,-1403)then return 0;end if;raise;
 end;
end;

/
