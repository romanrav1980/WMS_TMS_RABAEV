package body RRL_STOCK_PLAN_HELPER as
 procedure fence(p_plan in out nocopy json_array_t,p_kind varchar2,p_id varchar2,p_mode number default 4) is v json_object_t:=json_object_t();
 begin
  v.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key(p_kind,p_id)));v.put('mode',p_mode);p_plan.append(v);
 end;
 procedure anchor(p_plan in out nocopy json_array_t,p_rank number,p_kind varchar2,p_a varchar2,p_b varchar2 default null) is v json_object_t:=json_object_t();
 begin
  v.put('rank',p_rank);v.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key(p_kind,p_a,p_b)));p_plan.append(v);
 end;
 procedure row_key(p_plan in out nocopy json_array_t,p_table varchar2,p_id varchar2) is
 begin anchor(p_plan,20,'ROW',p_table,p_id);end;
 function decimal_text(p_value number) return varchar2 is v varchar2(200);
 begin
  v:=to_char(p_value,'TM9','NLS_NUMERIC_CHARACTERS=''.,''');
  if substr(v,1,1)='.' then return '0'||v;end if;
  if substr(v,1,2)='-.' then return '-0'||substr(v,2);end if;
  return v;
 end;
 procedure stock_closure(p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,
  p_uid varchar2,p_article varchar2,p_from varchar2,p_to varchar2) is
 begin
  for h in(select HU_LINK_ID,PARENT_UID,level DEPTH,connect_by_iscycle CYCLIC from RRL_WMS_HU_LINK
   start with ACTIVE_FLAG=1 and (CHILD_PALLET_UID=p_uid or CHILD_CASE_TASK_ID in
    (select CASE_PICK_TASK_ID from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid))
   connect by nocycle prior PARENT_UID=CHILD_PALLET_UID and ACTIVE_FLAG=1) loop
   if h.DEPTH>16 or h.CYCLIC=1 then raise_application_error(-20886,'HU_ANCESTOR_CYCLE_OR_DEPTH_BOUND');end if;
   anchor(p_resources,30,'HU',h.PARENT_UID);row_key(p_resources,'RRL_PALLETS',h.PARENT_UID);
   row_key(p_resources,'RRL_WMS_HU_LINK',decimal_text(h.HU_LINK_ID));
  end loop;
  fence(p_policies,'CONFIG','WAREHOUSE');fence(p_policies,'SKU',p_article);
  if p_from is not null then fence(p_policies,'CELL',p_from);anchor(p_resources,40,'SLOT','CELL:'||p_from);end if;
  if p_to is not null then fence(p_policies,'CELL',p_to);anchor(p_resources,40,'SLOT','CELL:'||p_to);end if;
  anchor(p_resources,30,'HU',p_uid);anchor(p_resources,50,'STOCK',p_uid);
  for r in(select RESERVATION_ID,CELL_SLOT_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,RESERVATION_DOMAIN from RRL_STOCK_RESERVATION
    where UID_PALLET=p_uid and STATUS in('ACTIVE','ALLOCATED','PICKING') and RESERVATION_KIND='HARD') loop
   if r.SOURCE_DOC_TYPE='PICK_WAVE' then row_key(p_resources,'RRL_PICK_WAVE',decimal_text(r.SOURCE_DOC_ID));
   elsif r.SOURCE_DOC_TYPE='PICK_PLAN' then row_key(p_resources,'RRL_PICK_PLAN',decimal_text(r.SOURCE_DOC_ID));
   elsif r.SOURCE_DOC_TYPE='PRODUCTION_ORDER' then row_key(p_resources,'RRL_PRODUCTION_ORDER',decimal_text(r.SOURCE_DOC_ID));end if;
   row_key(p_resources,'RRL_STOCK_RESERVATION',decimal_text(r.RESERVATION_ID));
   if r.SOURCE_DOC_TYPE='PICK_WAVE' and r.RESERVATION_DOMAIN='PICKING' and r.SOURCE_LINE_ID is not null then
    row_key(p_resources,'RRL_PICK_TASK',decimal_text(r.SOURCE_LINE_ID));end if;

   if r.CELL_SLOT_ID is not null then anchor(p_resources,40,'SLOT',decimal_text(r.CELL_SLOT_ID));end if;
  end loop;
  for c in(select TASK_ID,CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=p_uid and STATUS='OCCUPIED') loop
   row_key(p_resources,'RRL_RECEIPT_SLOT_CLAIM',decimal_text(c.TASK_ID));
   anchor(p_resources,40,'SLOT',decimal_text(c.CELL_SLOT_ID));
  end loop;
  for u in(select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and STOCK_STATUS!='ISSUED') loop
   if u.PHYSICAL_UNIT_KEY is null then raise_application_error(-20884,'COMPOSITION_BINDING_REQUIRED');end if;
   anchor(p_resources,60,'UNIT',u.PHYSICAL_UNIT_KEY);
  end loop;
 end;
end;
