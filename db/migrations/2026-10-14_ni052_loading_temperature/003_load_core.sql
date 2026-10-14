create or replace package body RRL_STOCK_HU_LOAD_CORE as
 procedure compile_load(p_request clob,p_snapshot clob,p_shipments clob,f in out nocopy json_array_t,r in out nocopy json_array_t,p_domain out json_object_t) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');ctx json_object_t;
  tree json_object_t:=json_object_t.parse(p_snapshot);measure json_object_t;tt RRL_TRANSPORT_TASK%rowtype;veh RRL_TR_VEHICLE%rowtype;
  mass_no number;volume_no number;width_no number;depth_no number;height_no number;ware_no number;blocked_no number;n number;trip_no number:=0;lower_mass number:=0;node_json json_object_t;node_array json_array_t;op varchar2(100):=d.get_string('operation_id');ids json_array_t:=json_array_t();destinations json_array_t:=json_array_t();destination json_object_t;j json_object_t;physical_boxes json_array_t;destination_wire clob;thermal_value json_object_t;
 begin
  if not m.has('loading_context') then p_domain:=null;return;end if;
  ctx:=m.get_object('loading_context');
  trip_no:=ctx.get_number('transport_task_id');select * into tt from RRL_TRANSPORT_TASK where ID=trip_no;
  select * into veh from RRL_TR_VEHICLE where NUM=tt.TRANSPORT and nvl(DELETED,0)=0;
  if tt.CONDITION is null or tt.CONDITION!=unistr('\0421\043F\043B\0430\043D\0438\0440\043E\0432\0430\043D') or nvl(tt.DELETED,0)!=0 or tt.DOCK is null then raise_application_error(-20886,'LOAD_ACTIVE_TRIP_VEHICLE_DOCK_REQUIRED');end if;
  if ctx.get_string('scan_vehicle') is null or ctx.get_string('scan_vehicle')!=tt.TRANSPORT or ctx.get_string('scan_dock') is null or ctx.get_string('scan_dock')!=tt.DOCK then raise_application_error(-20886,'LOAD_VEHICLE_DOCK_SCAN_REQUIRED');end if;
  if nvl(veh.BLOCKED,0)!=0 or nvl(veh.WORKING_NOW,0)!=1 or veh.PALLETS is null or veh.PALLETS<1 or veh.MAX_WEIGHT_KG is null or veh.MAX_WEIGHT_KG<=0 then raise_application_error(-20886,'LOAD_ACTIVE_VEHICLE_CAPACITY_REQUIRED');end if;
  select WARE_ID,nvl(DOCK_IS_BLOCKED,0) into ware_no,blocked_no from RRL_TT_DOCK where DOCK=tt.DOCK;
  if ware_no!=tree.get_number('warehouse') or blocked_no!=0 then raise_application_error(-20886,'LOAD_CURRENT_WAREHOUSE_DOCK_REQUIRED');end if;
  measure:=ctx.get_object('measurements');
  if measure.get_string('origin') is null or measure.get_string('origin')!='MANUAL_CONFIRMED' or measure.get_number('content_version') is null or measure.get_number('content_version')!=treat(tree.get_array('nodes').get(0) as json_object_t).get_number('version') then raise_application_error(-20886,'LOAD_CURRENT_MEASUREMENTS_REQUIRED');end if;
  mass_no:=RRL_STOCK_MATH.quantity(measure.get_string('gross_weight_kg'));width_no:=RRL_STOCK_MATH.quantity(measure.get_string('width_m'));depth_no:=RRL_STOCK_MATH.quantity(measure.get_string('depth_m'));height_no:=RRL_STOCK_MATH.quantity(measure.get_string('height_m'));
  if mass_no is null or width_no is null or depth_no is null or height_no is null or least(mass_no,width_no,depth_no,height_no)<=0 then raise_application_error(-20886,'LOAD_POSITIVE_SI_MEASUREMENTS_REQUIRED');end if;
  node_array:=tree.get_array('nodes');
  for i in 0..node_array.get_size-1 loop node_json:=treat(node_array.get(i) as json_object_t);
   lower_mass:=lower_mass+nvl(node_json.get_number('tare_weight_kg'),0);
   if node_json.get_string('kind')='STOCK' and node_json.get_string('base_uom')='KG' then lower_mass:=lower_mass+RRL_STOCK_MATH.quantity(node_json.get_string('quantity'));end if;
  end loop;
  if mass_no<lower_mass then raise_application_error(-20886,'LOAD_GROSS_BELOW_NET_AND_TARE');end if;
  volume_no:=ceil(width_no*depth_no*height_no*1000000000)/1000000000;
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(veh.ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(tt.ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_DOCK',tt.DOCK);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',op);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TT.LOAD.HU:'||tree.get_string('root'));
  for sp in(select ID,TRANSTASK_ID,WARE_ID,ADDR from RRL_SBORKA_PALLETS where ID in(select ID from json_table(p_shipments,'$[*]' columns(ID number path '$.domain.document_id'))) order by ID) loop
   if sp.ADDR is null then raise_application_error(-20886,'LOAD_ST_DESTINATION_REQUIRED');end if;
   destination:=json_object_t();destination.put('id',sp.ID);destination.put('address',sp.ADDR);destinations.append(destination);
   if sp.TRANSTASK_ID is null or sp.TRANSTASK_ID!=tt.ID or sp.WARE_ID!=ware_no then raise_application_error(-20886,'LOAD_ALL_STS_ASSIGNED_TO_THIS_TRIP_REQUIRED');end if;
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TT.LOAD.ST:'||RRL_STOCK_PLAN_HELPER.decimal_text(sp.ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_ST',op||':'||RRL_STOCK_PLAN_HELPER.decimal_text(sp.ID));ids.append(sp.ID);
  end loop;
  if ids.get_size=0 or ids.get_size>200 then raise_application_error(-20881,'LOAD_MEMBER_ST_BOUND_200');end if;
  destination_wire:=destinations.to_clob;
  select count(*)into n from RRL_STORE_RECEIPT_POLICY where RECEIPT_MODE='WEIGHT_PHOTO'and STORE_ADDR in(select ADDR_TEXT from json_table(destination_wire,'$[*]'columns(ADDR_TEXT varchar2(255)path '$.address')));
  ctx.put('require_complete_box_mass',n>0);
  RRL_STOCK_LOAD_BOX_CORE.compile_boxes(p_snapshot,ctx.to_clob,op,mass_no,r,physical_boxes);
  RRL_STOCK_LOAD_BOX_CORE.assert_policy(destinations.to_clob,physical_boxes);
  RRL_STOCK_LOAD_THERMAL.compile_confirmation(ids.to_clob,veh.ID,ctx.to_clob,thermal_value);
  p_domain:=json_object_t();p_domain.put('trip',tt.ID);p_domain.put('vehicle_id',veh.ID);p_domain.put('vehicle',tt.TRANSPORT);p_domain.put('dock',tt.DOCK);p_domain.put('warehouse',ware_no);p_domain.put('uid',tree.get_string('root'));p_domain.put('case_task_id',tree.get_number('case_task_id'));p_domain.put('content_version',measure.get_number('content_version'));p_domain.put('mass_kg',RRL_STOCK_PLAN_HELPER.decimal_text(mass_no));p_domain.put('volume_m3',RRL_STOCK_PLAN_HELPER.decimal_text(volume_no));p_domain.put('members',ids);p_domain.put('destinations',destinations);p_domain.put('physical_boxes',physical_boxes);
  if thermal_value is null then p_domain.put_null('temperature_at_loading');else p_domain.put('temperature_at_loading',thermal_value);end if;
 exception when no_data_found then raise_application_error(-20886,'LOAD_TRIP_VEHICLE_DOCK_CONFIGURATION_REQUIRED');
 end;
 procedure begin_load(p_domain clob) is
  j json_object_t:=json_object_t.parse(p_domain);tt RRL_TRANSPORT_TASK%rowtype;veh RRL_TR_VEHICLE%rowtype;ware_no number;blocked_no number;places number;mass_no number;
  trip_no number:=j.get_number('trip');vehicle_no number:=j.get_number('vehicle_id');dock_name varchar2(50):=j.get_string('dock');thermal_wire clob;thermal_element json_element_t;
 begin
  RRL_STOCK_LOAD_BOX_CORE.assert_policy(j.get_array('destinations').to_clob,j.get_array('physical_boxes'));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(vehicle_no)));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(trip_no)));
  select * into veh from RRL_TR_VEHICLE where ID=vehicle_no for update;
  select * into tt from RRL_TRANSPORT_TASK where ID=trip_no for update;
  select WARE_ID,nvl(DOCK_IS_BLOCKED,0) into ware_no,blocked_no from RRL_TT_DOCK where DOCK=dock_name for update;
  if tt.CONDITION is null or tt.CONDITION!=unistr('\0421\043F\043B\0430\043D\0438\0440\043E\0432\0430\043D') or nvl(tt.DELETED,0)!=0 or tt.TRANSPORT!=j.get_string('vehicle') or tt.DOCK!=dock_name or veh.NUM!=tt.TRANSPORT
   or nvl(veh.BLOCKED,0)!=0 or nvl(veh.WORKING_NOW,0)!=1 or nvl(veh.DELETED,0)!=0 or ware_no!=j.get_number('warehouse') or blocked_no!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: load trip/vehicle/dock');end if;
  select count(*),nvl(sum(GROSS_WEIGHT_KG),0) into places,mass_no from RRL_TT_HU_LOAD_FACT where TT_ID=trip_no and STATUS='LOADED';
  if veh.PALLETS is null or veh.MAX_WEIGHT_KG is null or places+1>veh.PALLETS or mass_no+RRL_STOCK_MATH.quantity(j.get_string('mass_kg'))>veh.MAX_WEIGHT_KG then raise_application_error(-20886,'LOAD_VEHICLE_PHYSICAL_CAPACITY_EXCEEDED');end if;
  select count(*) into places from RRL_TT_HU_LOAD_FACT where VEHICLE_ID=vehicle_no and TT_ID!=trip_no and STATUS='LOADED';
  if places>0 then raise_application_error(-20886,'LOAD_VEHICLE_HAS_ANOTHER_OPEN_TRIP');end if;
  if j.has('temperature_at_loading')then thermal_element:=j.get('temperature_at_loading');if not thermal_element.is_null then thermal_wire:=thermal_element.to_clob;end if;end if;
  RRL_STOCK_LOAD_THERMAL.assert_current(j.get_array('members').to_clob,vehicle_no,thermal_wire);
 end;
 procedure finish_load(p_domain clob,p_snapshot clob,p_operation varchar2,p_actor varchar2) is
  j json_object_t:=json_object_t.parse(p_domain);ids clob:=j.get_array('members').to_clob;trip_no number:=j.get_number('trip');root_uid varchar2(200):=j.get_string('uid');vehicle_no number:=j.get_number('vehicle_id');plate varchar2(50):=j.get_string('vehicle');dock_name varchar2(50):=j.get_string('dock');ware_no number:=j.get_number('warehouse');mass_no number:=RRL_STOCK_MATH.quantity(j.get_string('mass_kg'));volume_no number:=RRL_STOCK_MATH.quantity(j.get_string('volume_m3'));version_no number:=j.get_number('content_version');destinations clob:=j.get_array('destinations').to_clob;case_no number:=j.get_number('case_task_id');n number;thermal_element json_element_t;
 begin
  select count(*) into n from RRL_SBORKA_PALLETS where ID in(select ID from json_table(ids,'$[*]' columns(ID number path '$'))) and TRANSTASK_ID=trip_no and WARE_ID=ware_no and CONDITION=2;
  if n!=j.get_array('members').get_size then raise_application_error(-20890,'CLOSURE_CHANGED: physical load member assignment');end if;
  select count(*) into n from RRL_SBORKA_PALLETS sp join json_table(destinations,'$[*]' columns(ID number path '$.id',ADDR_TEXT varchar2(255) path '$.address')) frozen on frozen.ID=sp.ID and frozen.ADDR_TEXT=sp.ADDR
   where sp.TRANSTASK_ID=trip_no and sp.CONDITION=2;
  if n!=j.get_array('members').get_size then raise_application_error(-20890,'CLOSURE_CHANGED: physical load destinations');end if;
  if case_no is not null then root_uid:=null;end if;
  insert into RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID,TT_ID,ROOT_UID,VEHICLE_ID,VEHICLE_NUMBER,DOCK,WARE_ID,STATUS,GROSS_WEIGHT_KG,BOUNDING_VOLUME_M3,CONTENT_VERSION,COMPOSITION_JSON,LOADED_BY,ROOT_CASE_TASK_ID)
   values(p_operation,trip_no,root_uid,vehicle_no,plate,dock_name,ware_no,'LOADED',mass_no,volume_no,version_no,p_snapshot,p_actor,case_no);
  RRL_STOCK_LOAD_BOX_CORE.persist_boxes(p_operation,j.get_array('physical_boxes'),p_actor);
  if j.has('temperature_at_loading')then thermal_element:=j.get('temperature_at_loading');if not thermal_element.is_null then RRL_STOCK_LOAD_THERMAL.persist_confirmation(p_operation,thermal_element.to_clob,p_actor);end if;end if;
  for sp in(select ID,ADDR_TEXT from json_table(destinations,'$[*]' columns(ID number path '$.id',ADDR_TEXT varchar2(255) path '$.address')) order by ID) loop
   insert into RRL_TT_HU_LOAD_ST(LOAD_OPERATION_ID,SBORKA_PALLET_ID,DESTINATION_ADDR) values(p_operation,sp.ID,sp.ADDR_TEXT);
  end loop;
 end;
end;
/
