create or replace package body RRL_HU_CONSOL_LIST as
 function can_view(p_plan varchar2,p_actor nvarchar2)return number is begin
  RRL_HU_CONSOL_READ.assert_plan_scope(p_plan,p_actor,'warehouse_task_view');return 1;
 exception when others then
  if sqlcode in(-20882,-1403)then return 0;end if;raise;
 end;
 function page_json(p_actor nvarchar2,p_ware number,p_after varchar2,p_limit number,p_status varchar2)return clob is
  result_value json_object_t:=json_object_t();items json_array_t:=json_array_t();item json_object_t;
  last_value varchar2(100);more_value boolean:=false;member_count number;fetch_limit number:=p_limit+1;
 begin
  if p_limit is null or p_limit!=trunc(p_limit)or p_limit<1 or p_limit>50
   or p_ware is null or p_ware<1 or p_ware!=trunc(p_ware)
   or p_status is null or p_status not in('ACTIVE','CANCELLED','ALL')
   or(p_after is not null and not regexp_like(p_after,'^[A-Za-z0-9_.:-]{1,100}$'))then
   raise_application_error(-20881,'CONSOLIDATION_PAGE_INPUT_BOUND');end if;
  RRL_HU_CONSOL_READ.assert_scope(p_actor,p_ware,'warehouse_task_view');
  -- Current source/root authority is evaluated before the page limit. No hidden totals.
  -- Binary keyset order is independent of a caller's NLS_SORT/NLS_COMP settings.
  for r in(select PLAN_ID,ROOT_UID,TARGET_WARE_ID,TARGET_CELL,STATUS,PLAN_VERSION,UPDATED_AT
   from RRL_HU_CONSOL_PLAN
   where TARGET_WARE_ID=p_ware and(p_status='ALL'or STATUS=p_status)
    and(p_after is null or nlssort(PLAN_ID,'NLS_SORT=BINARY')>nlssort(p_after,'NLS_SORT=BINARY'))
    and RRL_HU_CONSOL_LIST.can_view(PLAN_ID,p_actor)=1
   order by nlssort(PLAN_ID,'NLS_SORT=BINARY')fetch first fetch_limit rows only)loop
   if items.get_size=p_limit then more_value:=true;exit;end if;
   select count(*)into member_count from RRL_HU_CONSOL_MEMBER where PLAN_ID=r.PLAN_ID;
   if member_count>200 then raise_application_error(-20881,'CONSOLIDATION_MEMBER_BOUND_200');end if;
   item:=json_object_t();item.put('plan_id',r.PLAN_ID);item.put('version',r.PLAN_VERSION);item.put('status',r.STATUS);
   item.put('root_identifier',r.ROOT_UID);item.put('warehouse_id',r.TARGET_WARE_ID);item.put('cell',r.TARGET_CELL);
   item.put('expected_count',member_count);item.put('updated_at',to_char(r.UPDATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
   items.append(item);last_value:=r.PLAN_ID;
  end loop;
  result_value.put('items',items);result_value.put('has_more',more_value);result_value.put('warehouse_id',p_ware);
  if more_value then result_value.put('next_after',last_value);else result_value.put_null('next_after');end if;
  result_value.put('stock_changed',false);return result_value.to_clob;
 end;
end;
/
