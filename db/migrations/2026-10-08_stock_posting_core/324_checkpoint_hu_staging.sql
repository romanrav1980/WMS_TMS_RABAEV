create or replace package RRL_STOCK_HU_SLOT authid definer
 accessible by(package RRL_STOCK_HU_CMD) as
 function target_json(p_tree clob,p_metadata clob,p_ignored_task number) return clob;
end;
/

create or replace package body RRL_STOCK_HU_SLOT as
 function target_json(p_tree clob,p_metadata clob,p_ignored_task number) return clob is
  j json_object_t:=json_object_t.parse(p_tree);m json_object_t:=json_object_t.parse(p_metadata);z json_object_t:=json_object_t();
  measures json_object_t;a json_array_t;x json_object_t;c RRL_CELLS%rowtype;s RRL_TOPOLOGY_CELL_SLOT%rowtype;
  v_slot number:=m.get_number('target_slot_id');v_task number:=m.get_number('planned_physical_task_id');v_count number;v_latest number;v_tc number;v_top_weight number;v_top_volume number;v_code varchar2(100);
  v_mass number;v_width number;v_depth number;v_height number;v_volume number;v_tare number:=0;v_lower number:=0;v_unit varchar2(2);v_scale number;v_article varchar2(160);v_cell varchar2(60):=m.get_string('target_cell');
 begin
  select * into c from RRL_CELLS where CELL=v_cell;
  if c.WARE_ID!=j.get_number('warehouse') or nvl(c.IS_SYSTEM,0)!=0 or nvl(c.OTBOR,0)!=0 then raise_application_error(-20886,'HU_ORDINARY_STORAGE_REQUIRED');end if;
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
   select count(*) into v_count from RRL_RECEIPT_SLOT_CLAIM where CELL_SLOT_ID=v_slot and STATUS in('RESERVED','OCCUPIED');
   if v_count>0 then raise_application_error(-20886,'HU_PHYSICAL_SLOT_OCCUPIED_OR_RESERVED');end if;
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
   if nvl(c.LIMIT_WEIGHT,0)>0 and v_mass>c.LIMIT_WEIGHT then raise_application_error(-20886,'HU_CELL_WEIGHT_EXCEEDED');end if;
   if nvl(c.LIMIT_HEIGHT,0)>0 then
    begin select HU_CELL_HEIGHT_UNIT into v_unit from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=c.WARE_ID;
    exception when no_data_found then v_unit:=null;end;
    if v_unit is null then raise_application_error(-20886,'HU_LEGACY_CELL_HEIGHT_UNIT_REQUIRED');end if;
    v_scale:=case v_unit when 'M' then 1 when 'CM' then 0.01 when 'MM' then 0.001 end;
    if v_height>c.LIMIT_HEIGHT*v_scale then raise_application_error(-20886,'HU_CELL_HEIGHT_EXCEEDED');end if;
   end if;
   if v_slot is not null then
    if(nvl(v_top_weight,0)>0 and v_mass>v_top_weight) or(nvl(v_top_volume,0)>0 and v_volume>v_top_volume) then raise_application_error(-20886,'HU_TOPOLOGY_CELL_WEIGHT_OR_VOLUME_EXCEEDED');end if;
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
