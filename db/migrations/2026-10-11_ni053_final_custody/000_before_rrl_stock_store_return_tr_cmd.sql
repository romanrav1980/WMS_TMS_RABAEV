create or replace package RRL_STOCK_STORE_RETURN_TR_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_STORE_RETURN_TR_CMD as
 procedure describe_plan(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v_approval varchar2(100):=d.get_object('source').get_string('approval_operation_id');
 v_trip number:=m.get_number('task_id');tt RRL_TRANSPORT_TASK%rowtype;veh RRL_TR_VEHICLE%rowtype;approved RRL_STORE_RETURN_APPROVAL%rowtype;sap RRL_STORE_RETURN_SAP%rowtype;
 v_store varchar2(255);v_qty number:=RRL_STOCK_MATH.quantity(m.get_string('gross_weight_kg'));v_places number:=m.get_number('physical_places');
 v_loaded_count number;v_loaded_mass number;v_return_count number;v_return_mass number;n number;
 begin
 if RRL_HAS_WRIGHT(p_actor,'store_return_transport')!=1 then raise_application_error(-20882,'STORE_RETURN_TRANSPORT_FORBIDDEN');end if;
 if v_trip is null or v_trip<1 or v_trip!=trunc(v_trip) or v_places is null or v_places<1 or v_places>200 or v_places!=trunc(v_places) then raise_application_error(-20886,'STORE_RETURN_TRIP_PHYSICAL_PLACES_REQUIRED');end if;
 select * into approved from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=v_approval;
 select * into sap from RRL_STORE_RETURN_SAP where APPROVAL_OPERATION_ID=v_approval;
 select STORE_ADDR into v_store from RRL_STORE_RECEIPT_FACT where OPERATION_ID=approved.RECEIPT_OPERATION_ID;
 select * into tt from RRL_TRANSPORT_TASK where ID=v_trip;
 select * into veh from RRL_TR_VEHICLE where NUM=tt.TRANSPORT and nvl(DELETED,0)=0;
 if tt.CONDITION is null or tt.CONDITION not in(unistr('\0421\043F\043B\0430\043D\0438\0440\043E\0432\0430\043D'),unistr('\041E\0442\0433\0440\0443\0436\0435\043D')) or nvl(tt.DELETED,0)!=0 or tt.VODITEL_ID is null
 or nvl(veh.BLOCKED,0)!=0 or nvl(veh.WORKING_NOW,0)!=1 or veh.PALLETS is null or veh.PALLETS<=0 or veh.MAX_WEIGHT_KG is null or veh.MAX_WEIGHT_KG<=0 then raise_application_error(-20886,'STORE_RETURN_ACTIVE_TRIP_VEHICLE_CAPACITY_REQUIRED');end if;
 select count(*) into n from RRL_TR_VODITEL where ID=tt.VODITEL_ID;
 if n!=1 then raise_application_error(-20886,'STORE_RETURN_ACTUAL_DRIVER_REQUIRED');end if;
 select count(*) into n from RRL_SBORKA_PALLETS where TRANSTASK_ID=v_trip and ADDR=v_store;
 if n=0 then raise_application_error(-20886,'STORE_RETURN_STORE_NOT_ON_EXISTING_TRIP');end if;
 select count(*) into n from RRL_STORE_RETURN_TRANSPORT where APPROVAL_OPERATION_ID=v_approval;
 if n!=0 then raise_application_error(-20886,'STORE_RETURN_ALREADY_PLANNED');end if;
 select count(*),nvl(sum(GROSS_WEIGHT_KG),0) into v_loaded_count,v_loaded_mass from RRL_TT_HU_LOAD_FACT where TT_ID=v_trip and STATUS in('LOADED','DEPARTED');
 select count(*),nvl(sum(PHYSICAL_PLACES),0),nvl(sum(GROSS_WEIGHT_KG),0) into n,v_return_count,v_return_mass from RRL_STORE_RETURN_TRANSPORT where TT_ID=v_trip;
 if n>=200 then raise_application_error(-20881,'STORE_RETURN_TRIP_PLAN_BOUND_200');end if;
 if v_loaded_count+v_return_count+v_places>veh.PALLETS or v_loaded_mass+v_return_mass+v_qty>veh.MAX_WEIGHT_KG then raise_application_error(-20886,'STORE_RETURN_CONSERVATIVE_CAPACITY_EXCEEDED');end if;
 p_domain:=json_object_t();p_domain.put('approval_operation_id',v_approval);p_domain.put('sap_operation_id',sap.OPERATION_ID);p_domain.put('receiving_warehouse',sap.WARE_ID);
 p_domain.put('task_id',v_trip);p_domain.put('vehicle_id',veh.ID);p_domain.put('vehicle_number',veh.NUM);p_domain.put('driver_id',tt.VODITEL_ID);p_domain.put('store_address',v_store);
 p_domain.put('gross_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));p_domain.put('physical_places',v_places);p_domain.put('existing_outbound_mass_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_loaded_mass));p_domain.put('existing_outbound_places',v_loaded_count);
 p_domain.put('previous_return_mass_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_return_mass));p_domain.put('previous_return_places',v_return_count);p_domain.put('capacity_basis','CONSERVATIVE_FULL_OUTBOUND');
 exception when no_data_found then raise_application_error(-20886,'STORE_RETURN_APPROVAL_SAP_TRIP_CONFIGURATION_REQUIRED');when too_many_rows then raise_application_error(-20886,'STORE_RETURN_CONFIGURATION_AMBIGUOUS');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
 describe_plan(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_APPROVAL',v.get_string('approval_operation_id'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_TRANSPORT',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('task_id')));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('vehicle_id')));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_dummy number;v_trip number;v_vehicle number;v_driver number;v_ware number;v_mass number;v_places number;v_approval varchar2(100);v_sap varchar2(100);v_plate varchar2(50);v_store varchar2(255);
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
 v_trip:=v.get_number('task_id');v_vehicle:=v.get_number('vehicle_id');
 select ID into v_dummy from RRL_TR_VEHICLE where ID=v_vehicle for update;
 select ID into v_dummy from RRL_TRANSPORT_TASK where ID=v_trip for update;
 describe_plan(p_request,p_actor,fresh);
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'STORE_RETURN_TRIP_OR_CAPACITY_CHANGED');end if;
 v_approval:=v.get_string('approval_operation_id');v_sap:=v.get_string('sap_operation_id');v_driver:=v.get_number('driver_id');v_ware:=v.get_number('receiving_warehouse');v_plate:=v.get_string('vehicle_number');v_store:=v.get_string('store_address');v_mass:=RRL_STOCK_MATH.quantity(v.get_string('gross_weight_kg'));v_places:=v.get_number('physical_places');
 insert into RRL_STORE_RETURN_TRANSPORT(OPERATION_ID,APPROVAL_OPERATION_ID,SAP_OPERATION_ID,TT_ID,VEHICLE_ID,VEHICLE_NUMBER,DRIVER_ID,STORE_ADDR,RECEIVING_WARE_ID,GROSS_WEIGHT_KG,PHYSICAL_PLACES,PLANNED_BY)
 values(op,v_approval,v_sap,v_trip,v_vehicle,v_plate,v_driver,v_store,v_ware,v_mass,v_places,p_actor);
 j.put('operation_id',op);j.put('approval_operation_id',v_approval);j.put('task_id',v_trip);j.put('receiving_warehouse',v_ware);j.put('status','PLANNED_PICKUP');j.put('capacity_basis','CONSERVATIVE_FULL_OUTBOUND');j.put('physical_pickup_confirmed',false);j.put('warehouse_stock_changed',false);p_result:=j.to_clob;
 end;
end;
/
