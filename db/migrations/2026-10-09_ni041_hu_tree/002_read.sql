create or replace package RRL_STOCK_HU_READ authid definer as
 function snapshot_json(p_uid varchar2,p_ignore_task number default null) return clob;
 procedure assert_quantity_write(p_uid varchar2);
end;
/
create or replace package body RRL_STOCK_HU_READ as
 function snapshot_json(p_uid varchar2,p_ignore_task number default null) return clob is
  j json_object_t:=json_object_t();nodes json_array_t:=json_array_t();edges json_array_t:=json_array_t();anc json_array_t:=json_array_t();x json_object_t;
  type seen_type is table of number index by varchar2(200);seen seen_type;
  v_leaf number:=0;v_count number:=0;v_cell varchar2(60);v_ware number;v_open number;
  procedure walk(p_id varchar2,p_depth number) is
   p RRL_PALLETS%rowtype;s RRL_REMAINS%rowtype;n number;cell_name varchar2(60);a json_object_t;b json_object_t;
  begin
   if p_depth>16 or seen.exists(p_id) then raise_application_error(-20886,'HU_CYCLE_OR_DEPTH_BOUND_16');end if;
   v_count:=v_count+1;if v_count>200 then raise_application_error(-20881,'HU_NODE_BOUND_200');end if;seen(p_id):=1;
   select * into p from RRL_PALLETS where UID_PALLET=p_id;
   a:=json_object_t();a.put('uid',p_id);a.put('kind',p.HU_KIND);a.put('type',p.HU_TYPE);a.put('version',p.HU_CONTENT_VERSION);
   a.put('sscc',p.SSCC);a.put('tare_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(p.HU_TARE_WEIGHT_KG));
   if p.HU_KIND='CONTAINER' then
    cell_name:=p.HU_CURRENT_CELL;
    select count(*) into n from RRL_REMAINS where UID_POLETA=p_id and (REMAIN!=0 or HARD_RESERVED_BASE!=0);
    if n>0 then raise_application_error(-20887,'HU_CONTAINER_HAS_QUANTITATIVE_STOCK');end if;
   else
    select count(*) into n from RRL_CASE_CARRIER_LOT where LOT_UID=p_id;
    if n>0 then raise_application_error(-20886,'HU_CASE_MEMBER_REQUIRES_CARRIER_ATTACHMENT');end if;
    select count(*) into n from RRL_REMAINS where UID_POLETA=p_id and REMAIN>0;
    if n!=1 then raise_application_error(-20886,'HU_LEAF_SINGLE_PHYSICAL_LOCATION_REQUIRED');end if;
    select * into s from RRL_REMAINS where UID_POLETA=p_id and REMAIN>0;
    cell_name:=s.CELL;v_leaf:=v_leaf+1;
    a.put('article',p.ARTICUL);a.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(s.REMAIN));
    a.put('hard_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(s.HARD_RESERVED_BASE));a.put('base_uom',s.BASE_UOM);
    a.put('stock_version',s.STOCK_VERSION);a.put('weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(p.WEIGHT_BRUTTO));
   end if;
   if cell_name is null then raise_application_error(-20886,'HU_PHYSICAL_LOCATION_REQUIRED');end if;
   if v_cell is null then v_cell:=cell_name;select WARE_ID into v_ware from RRL_CELLS where CELL=v_cell;
   elsif v_cell!=cell_name then raise_application_error(-20887,'HU_TREE_LOCATION_CONFLICT');end if;
   select count(*) into n from RRL_WAREHOUSE_TASK where UID_PALLET=p_id and STATUS not in('DONE','CANCELLED') and (p_ignore_task is null or TASK_ID!=p_ignore_task);
   a.put('open_task_count',n);a.put('cell',cell_name);a.put('depth',p_depth);nodes.append(a);
   for e in(select * from RRL_WMS_HU_LINK where PARENT_UID=p_id and ACTIVE_FLAG=1 order by HU_LINK_ID) loop
    if p.HU_KIND!='CONTAINER' then raise_application_error(-20887,'HU_QUANTITATIVE_LEAF_HAS_CHILDREN');end if;
    if e.CHILD_CASE_TASK_ID is not null then raise_application_error(-20886,'HU_CASE_SLICE_NOT_INSTALLED');end if;
    b:=json_object_t();b.put('id',e.HU_LINK_ID);b.put('parent',e.PARENT_UID);b.put('child',e.CHILD_PALLET_UID);b.put('version',e.LINK_VERSION);edges.append(b);
    walk(e.CHILD_PALLET_UID,p_depth+1);
   end loop;
  end;
 begin
  walk(p_uid,0);
  for h in(select PARENT_UID,level DEPTH,connect_by_iscycle CYCLIC from RRL_WMS_HU_LINK
   start with CHILD_PALLET_UID=p_uid and ACTIVE_FLAG=1
   connect by nocycle prior PARENT_UID=CHILD_PALLET_UID and ACTIVE_FLAG=1) loop
   if h.DEPTH>16 or h.CYCLIC=1 then raise_application_error(-20886,'HU_ANCESTOR_CYCLE_OR_DEPTH_BOUND');end if;
   x:=json_object_t();
   for p in(select HU_KIND,HU_CURRENT_CELL,HU_CONTENT_VERSION from RRL_PALLETS where UID_PALLET=h.PARENT_UID) loop
    if p.HU_KIND!='CONTAINER' or p.HU_CURRENT_CELL!=v_cell then raise_application_error(-20887,'HU_ANCESTOR_LOCATION_CONFLICT');end if;
    x.put('uid',h.PARENT_UID);x.put('version',p.HU_CONTENT_VERSION);x.put('cell',p.HU_CURRENT_CELL);
   end loop;
   select count(*) into v_open from RRL_WAREHOUSE_TASK where UID_PALLET=h.PARENT_UID and STATUS not in('DONE','CANCELLED') and (p_ignore_task is null or TASK_ID!=p_ignore_task);
   x.put('open_task_count',v_open);anc.append(x);
  end loop;
  j.put('root',p_uid);j.put('warehouse',v_ware);j.put('cell',v_cell);j.put('nodes',nodes);j.put('links',edges);j.put('ancestors',anc);
  j.put('leaf_count',v_leaf);j.put('top_place_count',case when anc.get_size=0 then 1 else 0 end);return j.to_clob;
 end;
 procedure assert_quantity_write(p_uid varchar2) is v_count number;v_op varchar2(100);v_command varchar2(80);
 begin
  select count(*) into v_count from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and (CHILD_PALLET_UID=p_uid
   or CHILD_CASE_TASK_ID in(select CASE_PICK_TASK_ID from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid));
  if v_count=0 then return;end if;
  v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');select COMMAND_TYPE into v_command from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
  if v_command not in('HU_MOVE','HU_TASK_COMPLETE') then raise_application_error(-20886,'NESTED_HU_REQUIRES_TOP_MOVE_OR_EXPLICIT_UNPACK');end if;
 end;
end;
/
