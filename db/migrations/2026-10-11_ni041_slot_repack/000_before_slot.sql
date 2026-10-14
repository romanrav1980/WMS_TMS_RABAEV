create or replace package RRL_STOCK_HU_SLOT authid definer
 accessible by(package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD) as
 function target_json(p_tree clob,p_metadata clob,p_ignored_task number,p_replace_root varchar2 default null,p_extra_weight number default 0,p_extra_volume number default 0) return clob;
end;
/

create or replace package body RRL_STOCK_HU_SLOT as
 procedure occupied_load(p_cell varchar2,p_ignored_task number,p_replace_root varchar2,p_weight out number,p_volume out number) is
  type keys is table of number index by varchar2(200);covered keys;tree json_object_t;a json_array_t;x json_object_t;
  roots number:=0;nodes number:=0;claims number;w number;v number;cv number;version_no number;stock_epoch number;unit_sig varchar2(64);saved_sig varchar2(64);unit_count number;
 begin
  p_weight:=0;p_volume:=0;
  if p_replace_root is not null then
   if substr(p_replace_root,1,5)='CASE:'then
    tree:=json_object_t.parse(RRL_STOCK_HU_READ.case_snapshot_json(to_number(substr(p_replace_root,6))));
   else tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(p_replace_root));end if;a:=tree.get_array('nodes');
   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);
    if x.get_string('kind')='STOCK' then covered(x.get_string('uid')):=1;end if;
   end loop;
  end if;
  for pp in(select UID_PALLET,HU_CONTENT_VERSION from RRL_PALLETS where HU_KIND='CONTAINER' and HU_CURRENT_CELL=p_cell and(p_replace_root is null or UID_PALLET!=p_replace_root)
   and not exists(select 1 from RRL_WMS_HU_LINK h where h.CHILD_PALLET_UID=UID_PALLET and h.ACTIVE_FLAG=1) order by UID_PALLET fetch first 201 rows only) loop
   roots:=roots+1;if roots>200 then raise_application_error(-20881,'HU_CELL_PLACE_BOUND_200');end if;
   select count(*),min(HU_GROSS_WEIGHT_KG),min(HU_BOUNDING_VOLUME_M3),min(HU_COMPOSITION_VERSION)
    into claims,w,v,cv from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=pp.UID_PALLET and CELL=p_cell and STATUS='OCCUPIED';
   if claims!=1 or w is null or v is null or cv is null or cv!=pp.HU_CONTENT_VERSION then raise_application_error(-20886,'HU_CELL_EXISTING_MEASUREMENTS_REQUIRED');end if;
   tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(pp.UID_PALLET));a:=tree.get_array('nodes');
   nodes:=nodes+a.get_size;if nodes>20000 then raise_application_error(-20881,'HU_CELL_COMPOSITION_BOUND_20000');end if;
   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);
    if x.get_string('kind')='STOCK' then covered(x.get_string('uid')):=1;end if;
   end loop;
   p_weight:=p_weight+w;p_volume:=p_volume+v;
  end loop;
  for pp in(select p.UID_PALLET,p.HU_CONTENT_VERSION,p.STOCK_COMPOSITION_VERSION from RRL_PALLETS p
   where p.HU_KIND='STOCK' and exists(select 1 from RRL_REMAINS r where r.UID_POLETA=p.UID_PALLET and r.CELL=p_cell and r.REMAIN>0)
   and(p_replace_root is null or p.UID_PALLET!=p_replace_root)
   and not exists(select 1 from RRL_WMS_HU_LINK h where h.CHILD_PALLET_UID=p.UID_PALLET and h.ACTIVE_FLAG=1)
   and not exists(select 1 from RRL_CASE_CARRIER_LOT ct where ct.LOT_UID=p.UID_PALLET)
   order by p.UID_PALLET fetch first 201 rows only) loop
   roots:=roots+1;if roots>200 then raise_application_error(-20881,'HU_CELL_PLACE_BOUND_200');end if;
   select count(*),min(HU_GROSS_WEIGHT_KG),min(HU_BOUNDING_VOLUME_M3),min(HU_COMPOSITION_VERSION),min(HU_STOCK_COMPOSITION_VERSION),min(HU_UNIT_SIGNATURE)
    into claims,w,v,cv,stock_epoch,saved_sig from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=pp.UID_PALLET and CELL=p_cell and STATUS='OCCUPIED';
   if claims!=1 or w is null or v is null or cv is null or cv!=pp.HU_CONTENT_VERSION or stock_epoch is null
    or stock_epoch!=pp.STOCK_COMPOSITION_VERSION or saved_sig is null then raise_application_error(-20886,'STOCK_PLACE_FRESH_MEASUREMENTS_REQUIRED');end if;
   RRL_STOCK_HU_UNIT_SIGNATURE.describe_units(pp.UID_PALLET,null,unit_sig,unit_count);
   nodes:=nodes+unit_count;if nodes>20000 then raise_application_error(-20881,'HU_CELL_COMPOSITION_BOUND_20000');end if;
   if saved_sig!=unit_sig then raise_application_error(-20886,'STOCK_PLACE_PHYSICAL_MEMBERS_CHANGED');end if;
   covered(pp.UID_PALLET):=1;p_weight:=p_weight+w;p_volume:=p_volume+v;
  end loop;
  for ct in(select CASE_PICK_TASK_ID,CONTENT_VERSION from RRL_CASE_PICK_TASK where CURRENT_CELL=p_cell and STATUS in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')
   and(p_replace_root is null or 'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(CASE_PICK_TASK_ID)!=p_replace_root)
   and not exists(select 1 from RRL_WMS_HU_LINK h where h.CHILD_CASE_TASK_ID=CASE_PICK_TASK_ID and h.ACTIVE_FLAG=1)
   order by CASE_PICK_TASK_ID fetch first 201 rows only) loop
   roots:=roots+1;if roots>200 then raise_application_error(-20881,'HU_CELL_PLACE_BOUND_200');end if;
   select count(*),min(HU_GROSS_WEIGHT_KG),min(HU_BOUNDING_VOLUME_M3),min(HU_COMPOSITION_VERSION) into claims,w,v,cv from RRL_RECEIPT_SLOT_CLAIM
    where HU_CASE_TASK_ID=ct.CASE_PICK_TASK_ID and CELL=p_cell and STATUS='OCCUPIED';
   if claims!=1 or w is null or v is null or cv is null or cv!=ct.CONTENT_VERSION then raise_application_error(-20886,'CASE_PLACE_FRESH_MEASUREMENTS_REQUIRED');end if;
   tree:=json_object_t.parse(RRL_STOCK_HU_READ.case_snapshot_json(ct.CASE_PICK_TASK_ID));a:=tree.get_array('nodes');
   nodes:=nodes+a.get_size;if nodes>20000 then raise_application_error(-20881,'HU_CELL_COMPOSITION_BOUND_20000');end if;
   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);if x.get_string('kind')='STOCK' then covered(x.get_string('uid')):=1;end if;end loop;
   p_weight:=p_weight+w;p_volume:=p_volume+v;
  end loop;
  for rr in(select UID_POLETA from RRL_REMAINS where CELL=p_cell and(REMAIN>0 or HARD_RESERVED_BASE>0) order by UID_POLETA fetch first 20001 rows only) loop
   if not covered.exists(rr.UID_POLETA) then raise_application_error(-20886,'HU_CELL_UNSLOTTED_OR_UNMEASURED_STOCK');end if;
  end loop;
  for wt in(select TASK_ID,TO_CELL_SLOT_ID,HU_MEASUREMENTS_JSON from RRL_WAREHOUSE_TASK where TO_CELL=p_cell and STATUS not in('DONE','CANCELLED')
   and(p_ignored_task is null or TASK_ID!=p_ignored_task) order by TASK_ID fetch first 201 rows only) loop
   roots:=roots+1;if roots>200 then raise_application_error(-20881,'HU_CELL_PLACE_BOUND_200');end if;
   if wt.TO_CELL_SLOT_ID is null or wt.HU_MEASUREMENTS_JSON is null then raise_application_error(-20886,'HU_CELL_ARRIVAL_MEASUREMENTS_REQUIRED');end if;
   x:=json_object_t.parse(wt.HU_MEASUREMENTS_JSON);
   w:=RRL_STOCK_MATH.quantity(x.get_string('gross_weight_kg'));
   v:=ceil(RRL_STOCK_MATH.quantity(x.get_string('width_m'))*RRL_STOCK_MATH.quantity(x.get_string('depth_m'))*RRL_STOCK_MATH.quantity(x.get_string('height_m'))*1000000000)/1000000000;
   if w is null or v is null or least(w,v)<=0 then raise_application_error(-20886,'HU_CELL_ARRIVAL_MEASUREMENTS_REQUIRED');end if;
   p_weight:=p_weight+w;p_volume:=p_volume+v;
  end loop;
  -- Other receipt claims cannot be converted to SI implicitly.
  select count(*) into claims from RRL_RECEIPT_SLOT_CLAIM cl where cl.CELL=p_cell and cl.STATUS in('RESERVED','OCCUPIED')
   and not exists(select 1 from RRL_CASE_PICK_TASK ct where ct.CASE_PICK_TASK_ID=cl.HU_CASE_TASK_ID and ct.CURRENT_CELL=p_cell)
   and not exists(select 1 from RRL_PALLETS pp where pp.UID_PALLET=cl.UID_PALLET and ((pp.HU_KIND='CONTAINER' and pp.HU_CURRENT_CELL=p_cell)
    or(pp.HU_KIND='STOCK' and cl.HU_STOCK_COMPOSITION_VERSION is not null and exists(select 1 from RRL_REMAINS rr where rr.UID_POLETA=pp.UID_PALLET and rr.CELL=p_cell and rr.REMAIN>0))))
   and(p_ignored_task is null or cl.TASK_ID!=p_ignored_task) and(p_replace_root is null or cl.UID_PALLET!=p_replace_root);
  if claims>0 then raise_application_error(-20886,'HU_CELL_OTHER_RECEIPT_MEASUREMENTS_REQUIRED');end if;
 end;
 function target_json(p_tree clob,p_metadata clob,p_ignored_task number,p_replace_root varchar2 default null,p_extra_weight number default 0,p_extra_volume number default 0) return clob is
  j json_object_t:=json_object_t.parse(p_tree);m json_object_t:=json_object_t.parse(p_metadata);z json_object_t:=json_object_t();
  measures json_object_t;a json_array_t;x json_object_t;c RRL_CELLS%rowtype;s RRL_TOPOLOGY_CELL_SLOT%rowtype;
  v_slot number:=m.get_number('target_slot_id');v_task number:=m.get_number('planned_physical_task_id');v_count number;v_latest number;v_tc number;v_top_weight number;v_top_volume number;v_code varchar2(100);
  v_existing_mass number:=0;v_existing_volume number:=0;v_mass number;v_width number;v_depth number;v_height number;v_volume number;v_tare number:=0;v_lower number:=0;v_unit varchar2(2);v_scale number;v_article varchar2(160);v_cell varchar2(60):=m.get_string('target_cell');
 begin
  if p_extra_weight is null or p_extra_volume is null or least(p_extra_weight,p_extra_volume)<0 then raise_application_error(-20871,'HU_EXTRA_LOAD_INVALID');end if;
  select * into c from RRL_CELLS where CELL=v_cell;
  if c.WARE_ID!=j.get_number('warehouse') or nvl(c.OTBOR,0)!=0 then raise_application_error(-20886,'HU_STORAGE_OR_CASE_STAGING_REQUIRED');end if;
  if nvl(c.IS_SYSTEM,0)!=0 then
   a:=j.get_array('nodes');
   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);
    if x.get_string('kind')='STOCK' and x.get_number('case_task_id') is null then raise_application_error(-20886,'HU_SYSTEM_TARGET_ONLY_CLOSED_CASE_CARRIERS');end if;
   end loop;
   z.put('target_role','CASE_CONTROL_OR_STAGING');
  else z.put('target_role','ORDINARY_STORAGE');end if;
  if nvl(c.BLOCKED_FOR_REMAINS,0)!=0 or nvl(c.BLOCKED_FOR_POPOLNENIE,0)!=0 or nvl(c.BLOCKED_FOR_ACCEPT,0)!=0 then raise_application_error(-20879,'LOCATION_BLOCKED');end if;
  select max(TOPOLOGY_ID) into v_latest from RRL_WAREHOUSE_TOPOLOGY where WARE_ID=c.WARE_ID and STATUS='PUBLISHED';
  select count(*) into v_count from RRL_TOPOLOGY_CELL_SLOT sl join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=sl.TOPOLOGY_CELL_ID
   where sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT' and tc.ACTIVE=1 and tc.LEGACY_CELL_CODE=v_cell and tc.TOPOLOGY_ID=v_latest;
  if v_slot is null and v_count>0 then raise_application_error(-20886,'HU_PHYSICAL_SLOT_REQUIRED');end if;
  if v_slot is not null then
   if p_ignored_task is null and v_task is null then raise_application_error(-20886,'HU_SLOT_REQUIRES_EXISTING_TASK_PLAN');end if;
   begin
    select sl.* into s from RRL_TOPOLOGY_CELL_SLOT sl
     join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=sl.TOPOLOGY_CELL_ID
     where sl.CELL_SLOT_ID=v_slot and sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT' and tc.ACTIVE=1
      and tc.LEGACY_CELL_CODE=v_cell and tc.WARE_ID=c.WARE_ID and tc.TOPOLOGY_ID=v_latest;
   exception when no_data_found then raise_application_error(-20886,'HU_SLOT_NOT_CURRENT_STORAGE');end;
   v_code:=s.SLOT_CODE;
   select MAX_WEIGHT_KG,MAX_VOLUME_M3 into v_top_weight,v_top_volume from RRL_TOPOLOGY_CELL where TOPOLOGY_CELL_ID=s.TOPOLOGY_CELL_ID;
   if nvl(s.CAPACITY_QTY,1)<1 then raise_application_error(-20886,'HU_SLOT_ONE_PLACE_CAPACITY_REQUIRED');end if;
   select count(*) into v_count from RRL_RECEIPT_SLOT_CLAIM where CELL_SLOT_ID=v_slot and STATUS in('RESERVED','OCCUPIED') and(p_replace_root is null or UID_PALLET!=p_replace_root);
   if v_count>0 then raise_application_error(-20886,'HU_PHYSICAL_SLOT_OCCUPIED_OR_RESERVED');end if;
   select count(*) into v_count from RRL_WAREHOUSE_TASK where TO_CELL_SLOT_ID=v_slot and STATUS not in('DONE','CANCELLED') and(p_ignored_task is null or TASK_ID!=p_ignored_task);
   if v_count>0 then raise_application_error(-20886,'HU_PHYSICAL_SLOT_PLANNED_ARRIVAL');end if;
   z.put('slot_id',v_slot);z.put('slot_code',v_code);
  end if;
  if v_slot is not null or nvl(c.LIMIT_WEIGHT,0)>0 or nvl(c.LIMIT_HEIGHT,0)>0 then
   if not m.has('measurements') or m.get('measurements').is_null then raise_application_error(-20886,'HU_FRESH_MEASUREMENTS_REQUIRED');end if;
   measures:=m.get_object('measurements');
   if measures.get_string('origin')!='MANUAL_CONFIRMED' or measures.get_number('content_version') is null
    or measures.get_number('content_version')!=treat(j.get_array('nodes').get(0) as json_object_t).get_number('version')
    then raise_application_error(-20886,'HU_MEASUREMENT_CONTENT_VERSION_REQUIRED');end if;
   v_mass:=RRL_STOCK_MATH.quantity(measures.get_string('gross_weight_kg'));
   v_width:=RRL_STOCK_MATH.quantity(measures.get_string('width_m'));v_depth:=RRL_STOCK_MATH.quantity(measures.get_string('depth_m'));
   v_height:=RRL_STOCK_MATH.quantity(measures.get_string('height_m'));
   if v_mass is null or v_width is null or v_depth is null or v_height is null or least(v_mass,v_width,v_depth,v_height)<=0 then raise_application_error(-20886,'HU_POSITIVE_SI_MEASUREMENTS_REQUIRED');end if;
   v_volume:=ceil(v_width*v_depth*v_height*1000000000)/1000000000;
   a:=j.get_array('nodes');
   for i in 0..a.get_size-1 loop
    x:=treat(a.get(i) as json_object_t);v_tare:=v_tare+nvl(x.get_number('tare_weight_kg'),0);
    if x.get_string('kind')='STOCK' and x.get_string('base_uom')='KG' then v_lower:=v_lower+RRL_STOCK_MATH.quantity(x.get_string('quantity'));end if;
   end loop;
   if v_mass<v_tare+v_lower then raise_application_error(-20886,'HU_GROSS_WEIGHT_BELOW_NET_AND_TARE');end if;
   if v_slot is not null then occupied_load(v_cell,p_ignored_task,p_replace_root,v_existing_mass,v_existing_volume);end if;
   if nvl(c.LIMIT_WEIGHT,0)>0 and v_mass+v_existing_mass+p_extra_weight>c.LIMIT_WEIGHT then raise_application_error(-20886,'HU_CELL_WEIGHT_EXCEEDED');end if;
   if nvl(c.LIMIT_HEIGHT,0)>0 then
    begin select HU_CELL_HEIGHT_UNIT into v_unit from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=c.WARE_ID;
    exception when no_data_found then v_unit:=null;end;
    if v_unit is null then raise_application_error(-20886,'HU_LEGACY_CELL_HEIGHT_UNIT_REQUIRED');end if;
    v_scale:=case v_unit when 'M' then 1 when 'CM' then 0.01 when 'MM' then 0.001 end;
    if v_height>c.LIMIT_HEIGHT*v_scale then raise_application_error(-20886,'HU_CELL_HEIGHT_EXCEEDED');end if;
   end if;
   if v_slot is not null then
    if(nvl(v_top_weight,0)>0 and v_mass+v_existing_mass+p_extra_weight>v_top_weight) or(nvl(v_top_volume,0)>0 and v_volume+v_existing_volume+p_extra_volume>v_top_volume) then raise_application_error(-20886,'HU_TOPOLOGY_CELL_WEIGHT_OR_VOLUME_EXCEEDED');end if;
    if (nvl(s.CAPACITY_WEIGHT_KG,0)>0 and v_mass>s.CAPACITY_WEIGHT_KG)
     or(nvl(s.CAPACITY_VOLUME_M3,0)>0 and v_volume>s.CAPACITY_VOLUME_M3)
     or(nvl(s.WIDTH_M,0)>0 and v_width>s.WIDTH_M) or(nvl(s.DEPTH_M,0)>0 and v_depth>s.DEPTH_M)
     or(nvl(s.HEIGHT_M,0)>0 and v_height>s.HEIGHT_M) then raise_application_error(-20886,'HU_SLOT_WEIGHT_VOLUME_OR_DIMENSIONS_EXCEEDED');end if;
   end if;
   measures.put('bounding_volume_m3',RRL_STOCK_PLAN_HELPER.decimal_text(v_volume));z.put('measurements',measures);
  end if;
  a:=j.get_array('nodes');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if x.get_string('kind')='STOCK' then
    v_article:=x.get_string('article');
    select count(*) into v_count from RRL_RECEIPT_SKU_RULE r left join RRL_RECEIPT_CELL_RULE cr on cr.CELL=v_cell and cr.WARE_ID=c.WARE_ID
     where r.WARE_ID=c.WARE_ID and r.ARTICUL=v_article
      and ((r.TEMP_MIN is not null and(cr.TEMP_MIN is null or cr.TEMP_MIN<r.TEMP_MIN))
       or(r.TEMP_MAX is not null and(cr.TEMP_MAX is null or cr.TEMP_MAX>r.TEMP_MAX)));
    if v_count>0 then raise_application_error(-20886,'HU_TARGET_TEMPERATURE_RULE_FAILED');end if;
   end if;
  end loop;
  return z.to_clob;
 end;
end;
/
