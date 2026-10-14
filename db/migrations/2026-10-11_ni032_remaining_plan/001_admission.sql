-- Per-order and per-warehouse/SKU planning locks; existing stock lock order, no global CONFIG X.
create or replace package RRL_PICK_PLAN_ADMISSION authid definer as
 procedure begin_plan(p_order number,p_actor varchar2);
 procedure end_plan;
end;
/
create or replace package body RRL_PICK_PLAN_ADMISSION as
 procedure actor_scope(p_order number,p_actor varchar2) is ware number;uware number;grp varchar2(100);
 begin
  begin select WARE_ID into ware from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=p_order;
  exception when no_data_found then raise_application_error(-20886,'PICK_ORDER_IDENTITY_MISSING');end;
  if ware is null or ware<1 then raise_application_error(-20886,'PICK_ORDER_WARE_REQUIRED');end if;
  begin select WARE_ID,USER_GROUP into uware,grp from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  exception when no_data_found then raise_application_error(-20882,'PICK_PLAN_ACTIVE_ACTOR_REQUIRED');end;
  if nvl(upper(trim(grp)),'-')!='GLOBAL_ADMIN'and(uware is null or uware!=ware)then
   raise_application_error(-20882,'PICK_PLAN_CURRENT_WARE_FORBIDDEN');end if;
  if RRL_HAS_WRIGHT(p_actor,'pick_plan_create')!=1 then raise_application_error(-20882,'PICK_PLAN_CREATE_FORBIDDEN');end if;
 end;
 procedure begin_plan(p_order number,p_actor varchar2)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();ware number;state varchar2(20);
  n number:=0;article_count number:=0;stock_count number:=0;task_count number:=0;v_started boolean:=false;
 begin
  actor_scope(p_order,p_actor);
  select WARE_ID into ware from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=p_order;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(p_order));
  for line in(select CUSTOMER_ORDER_ROW_ID,ARTICUL from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=p_order and STATUS!='CANCELLED'
   order by CUSTOMER_ORDER_ROW_ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20881,'PICK_PLAN_ROW_BOUND_200');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(line.CUSTOMER_ORDER_ROW_ID));
   RRL_STOCK_PLAN_HELPER.fence(f,'SKU',line.ARTICUL);
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PICK.PLAN.WARESKU:'||RRL_STOCK_PLAN_HELPER.decimal_text(ware)||':'||line.ARTICUL);
  end loop;
  for pt in(select pt.PICK_TASK_ID,pt.PICK_PLAN_ID,pt.PICK_PLAN_LINE_ID from RRL_PICK_TASK pt join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
   join RRL_CUSTOMER_ORDER_ROW cr on cr.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID where cr.CUSTOMER_ORDER_ID=p_order
   order by pt.PICK_TASK_ID fetch first 2001 rows only)loop
   task_count:=task_count+1;if task_count>2000 then raise_application_error(-20881,'PICK_PLAN_HISTORY_TASK_BOUND_2000');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(pt.PICK_TASK_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(pt.PICK_PLAN_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_PLAN_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(pt.PICK_PLAN_LINE_ID));
  end loop;
  for wave in(select distinct wo.PICK_WAVE_ID from RRL_PICK_WAVE_ORDER wo where wo.CUSTOMER_ORDER_ID=p_order order by wo.PICK_WAVE_ID fetch first 201 rows only)loop
   article_count:=article_count+1;if article_count>200 then raise_application_error(-20881,'PICK_PLAN_WAVE_HISTORY_BOUND_200');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(wave.PICK_WAVE_ID));
  end loop;
  for stock in(select s.UID_POLETA,s.CELL from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
   join RRL_CELLS c on c.CELL=s.CELL where c.WARE_ID=ware and s.REMAIN>0 and exists(
    select 1 from RRL_CUSTOMER_ORDER_ROW cr where cr.CUSTOMER_ORDER_ID=p_order and cr.ARTICUL=p.ARTICUL and cr.STATUS!='CANCELLED')
   order by s.UID_POLETA,s.CELL fetch first 501 rows only)loop
   stock_count:=stock_count+1;if stock_count>500 then raise_application_error(-20881,'PICK_PLAN_SOURCE_STOCK_BOUND_500');end if;
   RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',stock.UID_POLETA);
  end loop;
  RRL_STOCK_LOCK_API.begin_plan;v_started:=true;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state!='ACTIVE'or state is null then raise_application_error(-20860,'PICK_PLAN_ACTIVE_RELEASE_REQUIRED');end if;
  actor_scope(p_order,p_actor);
 exception when others then if v_started then RRL_STOCK_LOCK_API.clear_plan;end if;raise;
 end;
 procedure end_plan is begin RRL_STOCK_LOCK_API.clear_plan;end;
end;
/
