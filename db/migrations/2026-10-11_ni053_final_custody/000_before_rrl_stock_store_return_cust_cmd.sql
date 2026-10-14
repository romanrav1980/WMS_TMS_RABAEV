create or replace package RRL_STOCK_STORE_RETURN_CUST_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_STORE_RETURN_CUST_CMD as
 procedure describe_context(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);s json_object_t:=d.get_object('source');m json_object_t:=d.get_object('metadata');v_kind varchar2(80):=d.get_string('command_type');
 v_transport varchar2(100):=s.get_string('transport_operation_id');v_handover varchar2(100):=s.get_string('handover_operation_id');transport RRL_STORE_RETURN_TRANSPORT%rowtype;handed RRL_STORE_RETURN_HANDOVER%rowtype;approved RRL_STORE_RETURN_APPROVAL%rowtype;
 tt RRL_TRANSPORT_TASK%rowtype;veh RRL_TR_VEHICLE%rowtype;binding RRL_TRANSPORT_DRIVER_USER%rowtype;
 n number;v_mass number;v_slots number;v_pallet varchar2(32767);v_outbound_mass number;v_outbound_places number;v_return_mass number;v_return_places number;
 begin
 if v_kind='STORE_RETURN_PICKUP' then select * into handed from RRL_STORE_RETURN_HANDOVER where OPERATION_ID=v_handover;v_transport:=handed.TRANSPORT_OPERATION_ID;end if;
 select * into transport from RRL_STORE_RETURN_TRANSPORT where OPERATION_ID=v_transport;
 select * into approved from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=transport.APPROVAL_OPERATION_ID;
 select * into tt from RRL_TRANSPORT_TASK where ID=transport.TT_ID;
 select * into veh from RRL_TR_VEHICLE where ID=transport.VEHICLE_ID;
 if tt.CONDITION is null or tt.CONDITION!=unistr('\041E\0442\0433\0440\0443\0436\0435\043D') or nvl(tt.DELETED,0)!=0 or tt.TRANSPORT is null or tt.TRANSPORT!=transport.VEHICLE_NUMBER or tt.VODITEL_ID is null or tt.VODITEL_ID!=transport.DRIVER_ID
 or veh.NUM!=transport.VEHICLE_NUMBER or nvl(veh.DELETED,0)!=0 or nvl(veh.BLOCKED,0)!=0 or nvl(veh.WORKING_NOW,0)!=1 or veh.PALLETS is null or veh.MAX_WEIGHT_KG is null then raise_application_error(-20886,'STORE_RETURN_CURRENT_DEPARTED_TRIP_REQUIRED');end if;
 select count(*) into n from RRL_TR_VODITEL where ID=transport.DRIVER_ID and nvl(DELETED,0)=0;
 if n!=1 then raise_application_error(-20886,'STORE_RETURN_CURRENT_ACTIVE_DRIVER_REQUIRED');end if;
 select count(*) into n from RRL_TT_HU_LOAD_FACT where VEHICLE_ID=veh.ID and TT_ID!=tt.ID and STATUS='LOADED';
 if n>0 then raise_application_error(-20886,'STORE_RETURN_VEHICLE_HAS_OTHER_OPEN_LOAD');end if;
 select nvl(sum(GROSS_WEIGHT_KG),0),count(*) into v_outbound_mass,v_outbound_places from RRL_TT_HU_LOAD_FACT where TT_ID=tt.ID and STATUS in('LOADED','DEPARTED');
 select nvl(sum(GROSS_WEIGHT_KG),0),nvl(sum(PHYSICAL_PLACES),0) into v_return_mass,v_return_places from RRL_STORE_RETURN_TRANSPORT where TT_ID=tt.ID;
 if v_outbound_mass+v_return_mass>veh.MAX_WEIGHT_KG or v_outbound_places+v_return_places>veh.PALLETS then raise_application_error(-20886,'STORE_RETURN_CURRENT_CAPACITY_EXCEEDED');end if;
 if transport.PHYSICAL_PLACES!=1 then raise_application_error(-20886,'STORE_RETURN_MULTI_PLACE_MANIFEST_REQUIRED');end if;
 if v_kind='STORE_RETURN_HANDOVER' then
  if RRL_HAS_WRIGHT(p_actor,'store_return_handover')!=1 then raise_application_error(-20882,'STORE_RETURN_HANDOVER_FORBIDDEN');end if;
  RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,transport.STORE_ADDR);
  v_pallet:=m.get_string('pallet_identifier');v_mass:=RRL_STOCK_MATH.quantity(m.get_string('gross_weight_kg'));v_slots:=m.get_number('physical_places');
  if trim(v_pallet) is null or lengthb(v_pallet)>200 or v_slots is null or v_slots!=transport.PHYSICAL_PLACES or v_mass>transport.GROSS_WEIGHT_KG then raise_application_error(-20886,'STORE_RETURN_PHYSICAL_PLACE_OR_PLAN_MISMATCH');end if;
  if m.get_string('base_uom') is null or m.get_string('base_uom')!=approved.BASE_UOM or RRL_STOCK_MATH.quantity(m.get_string('quantity'))!=approved.BASE_QTY then raise_application_error(-20886,'STORE_RETURN_FULL_APPROVED_QUANTITY_REQUIRED');end if;
  select count(*) into n from RRL_STORE_RETURN_HANDOVER where TRANSPORT_OPERATION_ID=v_transport;
  if n!=0 then raise_application_error(-20886,'STORE_RETURN_ALREADY_HANDED_OVER');end if;
 else
  if RRL_HAS_WRIGHT(p_actor,'driver_return_accept')!=1 then raise_application_error(-20882,'STORE_RETURN_DRIVER_ACCEPT_FORBIDDEN');end if;
  select * into binding from RRL_TRANSPORT_DRIVER_USER where DRIVER_ID=transport.DRIVER_ID and ACTIVE=1 and USER_ID=p_actor;
  select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and upper(trim(USER_GROUP))!='GLOBAL_ADMIN';
  if n!=1 then raise_application_error(-20882,'STORE_RETURN_DEDICATED_DRIVER_REQUIRED');end if;
  if p_actor=handed.HANDED_BY then raise_application_error(-20882,'STORE_RETURN_SEPARATE_HANDOVER_AND_DRIVER_REQUIRED');end if;
  if m.get_string('scan_vehicle') is null or m.get_string('scan_vehicle')!=veh.NUM or m.get_string('scan_pallet') is null or m.get_string('scan_pallet')!=handed.PALLET_IDENTIFIER then raise_application_error(-20886,'STORE_RETURN_DRIVER_VEHICLE_PALLET_SCAN_REQUIRED');end if;
  select count(*) into n from RRL_STORE_RETURN_PICKUP where HANDOVER_OPERATION_ID=v_handover;
  if n!=0 then raise_application_error(-20886,'STORE_RETURN_ALREADY_PICKED_UP');end if;
  v_pallet:=handed.PALLET_IDENTIFIER;v_mass:=handed.GROSS_WEIGHT_KG;v_slots:=handed.PHYSICAL_PLACES;
 end if;
 p_domain:=json_object_t();p_domain.put('transport_operation_id',v_transport);p_domain.put('approval_operation_id',transport.APPROVAL_OPERATION_ID);p_domain.put('task_id',tt.ID);p_domain.put('vehicle_id',veh.ID);p_domain.put('vehicle_number',veh.NUM);p_domain.put('driver_id',transport.DRIVER_ID);
 p_domain.put('pallet_identifier',v_pallet);p_domain.put('gross_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_mass));p_domain.put('physical_places',v_slots);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(approved.BASE_QTY));p_domain.put('base_uom',approved.BASE_UOM);
 if v_kind='STORE_RETURN_PICKUP' then p_domain.put('handover_operation_id',v_handover);p_domain.put('binding_version',binding.BINDING_VERSION);end if;
 exception when no_data_found then
  if v_kind='STORE_RETURN_PICKUP' then raise_application_error(-20882,'STORE_RETURN_BOUND_DRIVER_AND_HANDOVER_REQUIRED');else raise_application_error(-20886,'STORE_RETURN_CURRENT_SOURCE_CONFIGURATION_REQUIRED');end if;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();v_kind varchar2(80):=d.get_string('command_type');
 begin
 describe_context(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_TRANSPORT',v.get_string('transport_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('task_id')));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('vehicle_id')));
 if v_kind='STORE_RETURN_HANDOVER' then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_HANDOVER',p_operation);
 else
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_HANDOVER',v.get_string('handover_operation_id'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_PICKUP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_DRIVER_USER',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('driver_id')));
 end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');v_kind varchar2(80):=d.get_string('command_type');plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_dummy number;v_trip number;v_transport varchar2(100);v_handover varchar2(100);v_vehicle number;v_driver number;v_binding number;v_plate varchar2(50);v_mass number;v_slots number;v_pallet varchar2(200);
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
 v_vehicle:=v.get_number('vehicle_id');v_trip:=v.get_number('task_id');
 select ID into v_dummy from RRL_TR_VEHICLE where ID=v_vehicle for update;
 select ID into v_dummy from RRL_TRANSPORT_TASK where ID=v_trip for update;
 describe_context(p_request,p_actor,fresh);
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'STORE_RETURN_CUSTODY_SOURCE_CHANGED');end if;
 v_transport:=v.get_string('transport_operation_id');v_vehicle:=v.get_number('vehicle_id');v_driver:=v.get_number('driver_id');v_plate:=v.get_string('vehicle_number');
 v_mass:=RRL_STOCK_MATH.quantity(v.get_string('gross_weight_kg'));v_slots:=v.get_number('physical_places');v_pallet:=v.get_string('pallet_identifier');
 if v_kind='STORE_RETURN_HANDOVER' then
  insert into RRL_STORE_RETURN_HANDOVER(OPERATION_ID,TRANSPORT_OPERATION_ID,PALLET_IDENTIFIER,GROSS_WEIGHT_KG,PHYSICAL_PLACES,HANDED_BY)values(op,v_transport,v_pallet,v_mass,v_slots,p_actor);
  j.put('custody','STORE_PENDING_DRIVER');
 else
  v_handover:=v.get_string('handover_operation_id');v_binding:=v.get_number('binding_version');
  insert into RRL_STORE_RETURN_PICKUP(OPERATION_ID,HANDOVER_OPERATION_ID,DRIVER_ID,VEHICLE_ID,VEHICLE_NUMBER,BINDING_VERSION,TAKEN_BY)values(op,v_handover,v_driver,v_vehicle,v_plate,v_binding,p_actor);
  j.put('custody','VEHICLE');j.put('handover_operation_id',v_handover);
 end if;
 j.put('operation_id',op);j.put('transport_operation_id',v_transport);j.put('quantity',v.get_string('quantity'));j.put('base_uom',v.get_string('base_uom'));j.put('warehouse_stock_changed',false);p_result:=j.to_clob;
 end;
end;
/
