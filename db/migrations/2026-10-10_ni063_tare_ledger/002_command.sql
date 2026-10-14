create or replace function RRL_TARE_BALANCE_KEY(p_owner number,p_type number,p_condition varchar2,p_kind varchar2,p_id varchar2) return raw authid definer is
 a json_array_t:=json_array_t();
begin a.append(p_owner);a.append(p_type);a.append(p_condition);a.append(p_kind);a.append(p_id);
 return sys.dbms_crypto.hash(utl_i18n.string_to_raw(a.to_string,'AL32UTF8'),sys.dbms_crypto.hash_sh256);
end;
/
create or replace package RRL_STOCK_TARE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_TARE_CMD as
 procedure balance(p_key raw,p_qty out number,p_version out number) is
 begin select QUANTITY,BALANCE_VERSION into p_qty,p_version from RRL_TARE_BALANCE where BALANCE_KEY=p_key;
 exception when no_data_found then p_qty:=0;p_version:=0;end;
 function integer_qty(p_text varchar2,p_zero boolean default false) return number is v number;
 begin
 if p_text is null or not regexp_like(p_text,'^[0-9]{1,18}$') then raise_application_error(-20886,'TARE_INTEGER_QUANTITY_REQUIRED');end if;
 v:=to_number(p_text);if not p_zero and v=0 then raise_application_error(-20886,'TARE_POSITIVE_QUANTITY_REQUIRED');end if;return v;
 end;
 procedure warehouse_actor(p_actor varchar2,p_owner number) is n number;
 begin
 select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(upper(trim(USER_GROUP))='GLOBAL_ADMIN' or WARE_ID=p_owner);
 if n!=1 then raise_application_error(-20882,'TARE_WAREHOUSE_BINDING_REQUIRED');end if;
 end;
 procedure holder_actor(p_actor varchar2,p_kind varchar2,p_id varchar2,p_owner number,p_trip RRL_TRANSPORT_TASK%rowtype,p_right varchar2) is n number;
 begin
 if RRL_HAS_WRIGHT(p_actor,p_right)!=1 then raise_application_error(-20882,'TARE_PARTICIPANT_PERMISSION_REQUIRED');end if;
 if p_kind='WAREHOUSE' then warehouse_actor(p_actor,p_owner);
 elsif p_kind='VEHICLE' then
 select count(*) into n from RRL_TRANSPORT_DRIVER_USER b join RUSERS u on u.ID=b.USER_ID
 where b.DRIVER_ID=p_trip.VODITEL_ID and b.USER_ID=p_actor and b.ACTIVE=1 and nvl(u.DELETED,0)=0 and upper(trim(u.USER_GROUP))!='GLOBAL_ADMIN';
 if n!=1 then raise_application_error(-20882,'TARE_AUTHENTICATED_CURRENT_DRIVER_REQUIRED');end if;
 else RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,p_id);end if;
 end;
 procedure describe_command(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');s json_object_t:=d.get_object('source');kind varchar2(80):=d.get_string('command_type');
 v_owner number;v_type number;v_condition varchar2(10);v_from_kind varchar2(12);v_from_id varchar2(255);v_to_kind varchar2(12);v_to_id varchar2(255);
 v_from raw(32);v_to raw(32);v_from_qty number;v_from_version number;v_to_qty number;v_to_version number;v_qty number;v_tt number;v_vehicle number;v_store varchar2(255);v_reason varchar2(2000);v_ref varchar2(255);n number;
 trip RRL_TRANSPORT_TASK%rowtype;vehicle RRL_TR_VEHICLE%rowtype;offer RRL_TARE_OFFER%rowtype;
 begin
 p_domain:=json_object_t();
 if kind='TARE_COUNT' then
  if RRL_HAS_WRIGHT(p_actor,'tare_adjust')!=1 then raise_application_error(-20882,'TARE_ADJUSTMENT_PERMISSION_REQUIRED');end if;
  v_owner:=m.get_number('owner_ware_id');v_type:=m.get_number('pallet_type_id');v_condition:=m.get_string('condition');
  warehouse_actor(p_actor,v_owner);v_to_kind:='WAREHOUSE';v_to_id:=RRL_STOCK_PLAN_HELPER.decimal_text(v_owner);
  v_qty:=integer_qty(m.get_string('observed_quantity'),true);v_reason:=m.get_string('reason');v_ref:=m.get_string('decision_reference');
  if trim(v_reason) is null or lengthb(v_reason)>2000 or trim(v_ref) is null or lengthb(v_ref)>255 then raise_application_error(-20886,'TARE_ADJUSTMENT_REASON_DECISION_REQUIRED');end if;
 else
  if kind='TARE_ACCEPT' then
   select * into offer from RRL_TARE_OFFER where OPERATION_ID=s.get_string('offer_operation_id');
   select count(*) into n from RRL_TARE_ACCEPT where OFFER_OPERATION_ID=offer.OPERATION_ID;
   if n!=0 then raise_application_error(-20886,'TARE_OFFER_ALREADY_ACCEPTED');end if;
   v_owner:=offer.OWNER_WARE_ID;v_type:=offer.PALLET_TYPE_ID;v_condition:=offer.CONDITION_CODE;
   v_from_kind:=offer.FROM_KIND;v_from_id:=offer.FROM_ID;v_to_kind:=offer.TO_KIND;v_to_id:=offer.TO_ID;v_tt:=offer.TT_ID;v_vehicle:=offer.VEHICLE_ID;v_store:=offer.STORE_ADDR;
   v_qty:=integer_qty(m.get_string('accepted_quantity'));
   if v_qty>offer.QUANTITY then raise_application_error(-20886,'TARE_ACCEPTED_QUANTITY_EXCEEDS_OFFER');end if;
   if offer.OFFERED_BY=p_actor then raise_application_error(-20882,'TARE_TWO_DIFFERENT_PARTICIPANTS_REQUIRED');end if;
   p_domain.put('offer_operation_id',offer.OPERATION_ID);p_domain.put('offered_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(offer.QUANTITY));
  else
   v_owner:=m.get_number('owner_ware_id');v_type:=m.get_number('pallet_type_id');v_condition:=m.get_string('condition');
   v_from_kind:=m.get_string('from_kind');v_from_id:=m.get_string('from_id');v_to_kind:=m.get_string('to_kind');v_to_id:=m.get_string('to_id');
   v_tt:=s.get_number('task_id');v_qty:=integer_qty(m.get_string('quantity'));
  end if;
  if v_from_kind||'>'||v_to_kind not in('WAREHOUSE>VEHICLE','VEHICLE>STORE','STORE>VEHICLE','VEHICLE>WAREHOUSE') then raise_application_error(-20886,'TARE_SUPPORTED_PHYSICAL_TRANSFER_REQUIRED');end if;
  select * into trip from RRL_TRANSPORT_TASK where ID=v_tt;
  select * into vehicle from RRL_TR_VEHICLE where NUM=trip.TRANSPORT and nvl(DELETED,0)=0;
  if nvl(trip.DELETED,0)!=0 or trip.CONDITION is null or trip.CONDITION not in(unistr('\0421\043F\043B\0430\043D\0438\0440\043E\0432\0430\043D'),unistr('\041E\0442\0433\0440\0443\0436\0435\043D'))
   or nvl(vehicle.BLOCKED,0)!=0 or nvl(vehicle.WORKING_NOW,0)!=1 or trip.VODITEL_ID is null then raise_application_error(-20886,'TARE_CURRENT_ACTIVE_TRIP_VEHICLE_DRIVER_REQUIRED');end if;
  select count(*) into n from RRL_TR_VODITEL where ID=trip.VODITEL_ID and nvl(DELETED,0)=0;
  if n!=1 then raise_application_error(-20886,'TARE_ACTIVE_DRIVER_REQUIRED');end if;
  if kind='TARE_ACCEPT' and(v_vehicle!=vehicle.ID or offer.VEHICLE_NUMBER!=vehicle.NUM) then raise_application_error(-20886,'TARE_ORIGINAL_TRIP_VEHICLE_CHANGED');end if;
  v_vehicle:=vehicle.ID;
  if(v_from_kind='VEHICLE' and v_from_id!=RRL_STOCK_PLAN_HELPER.decimal_text(v_vehicle)) or(v_to_kind='VEHICLE' and v_to_id!=RRL_STOCK_PLAN_HELPER.decimal_text(v_vehicle))
   or(v_from_kind='WAREHOUSE' and v_from_id!=RRL_STOCK_PLAN_HELPER.decimal_text(v_owner)) or(v_to_kind='WAREHOUSE' and v_to_id!=RRL_STOCK_PLAN_HELPER.decimal_text(v_owner)) then raise_application_error(-20886,'TARE_CURRENT_HOLDER_ID_REQUIRED');end if;
  if v_from_kind='STORE' or v_to_kind='STORE' then
   v_store:=case when v_from_kind='STORE' then v_from_id else v_to_id end;
   if trip.CONDITION!=unistr('\041E\0442\0433\0440\0443\0436\0435\043D') then raise_application_error(-20886,'TARE_STORE_TRANSFER_DEPARTED_TRIP_REQUIRED');end if;
   select count(*) into n from RRL_SBORKA_PALLETS where TRANSTASK_ID=trip.ID and ADDR=v_store;
   if n=0 then raise_application_error(-20886,'TARE_STORE_NOT_IN_EXISTING_TRIP');end if;
  end if;
  if m.get_string('scan_vehicle') is null or m.get_string('scan_vehicle')!=vehicle.NUM then raise_application_error(-20886,'TARE_CURRENT_VEHICLE_SCAN_REQUIRED');end if;
  holder_actor(p_actor,case when kind='TARE_ACCEPT' then v_to_kind else v_from_kind end,case when kind='TARE_ACCEPT' then v_to_id else v_from_id end,v_owner,trip,case when kind='TARE_ACCEPT' then 'tare_accept' else 'tare_offer' end);
  v_from:=RRL_TARE_BALANCE_KEY(v_owner,v_type,v_condition,v_from_kind,v_from_id);balance(v_from,v_from_qty,v_from_version);
  if v_from_qty<v_qty then raise_application_error(-20886,'TARE_SOURCE_QUANTITY_UNAVAILABLE');end if;
  p_domain.put('from_key',rawtohex(v_from));p_domain.put('from_kind',v_from_kind);p_domain.put('from_id',v_from_id);p_domain.put('from_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_from_qty));p_domain.put('from_version',v_from_version);
  p_domain.put('task_id',trip.ID);p_domain.put('vehicle_id',vehicle.ID);p_domain.put('vehicle_number',vehicle.NUM);p_domain.put('driver_id',trip.VODITEL_ID);p_domain.put('store_address',v_store);
 end if;
 if v_owner is null or v_type is null or v_condition is null or v_condition not in('GOOD','DAMAGED') or v_to_id is null or v_from_id is null and kind!='TARE_COUNT' then raise_application_error(-20886,'TARE_OWNER_TYPE_CONDITION_HOLDER_REQUIRED');end if;
 select count(*) into n from RRL_WARES where ID=v_owner;if n!=1 then raise_application_error(-20886,'TARE_OWNER_WAREHOUSE_REQUIRED');end if;
 select count(*) into n from RRL_PALLET_TYPE where PALLET_TYPE_ID=v_type and ACTIVE=1;if n!=1 then raise_application_error(-20886,'TARE_ACTIVE_EXISTING_PALLET_TYPE_REQUIRED');end if;
 v_to:=RRL_TARE_BALANCE_KEY(v_owner,v_type,v_condition,v_to_kind,v_to_id);balance(v_to,v_to_qty,v_to_version);
 if kind='TARE_COUNT' and(m.get_number('expected_version') is null or m.get_number('expected_version')!=v_to_version)then raise_application_error(-20886,'TARE_COUNT_VERSION_CONFLICT');end if;
 p_domain.put('owner_ware_id',v_owner);p_domain.put('pallet_type_id',v_type);p_domain.put('condition',v_condition);p_domain.put('to_key',rawtohex(v_to));p_domain.put('to_kind',v_to_kind);p_domain.put('to_id',v_to_id);
 p_domain.put('to_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_to_qty));p_domain.put('to_version',v_to_version);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
 if kind='TARE_COUNT' then p_domain.put('reason',v_reason);p_domain.put('decision_reference',v_ref);end if;
 exception when no_data_found then raise_application_error(-20886,'TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER_REQUIRED');when too_many_rows then raise_application_error(-20886,'TARE_EXISTING_VEHICLE_IDENTITY_AMBIGUOUS');end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();kind varchar2(80):=d.get_string('command_type');
 begin
 describe_command(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',v.get_string('to_key'));
 if kind!='TARE_COUNT' then
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',v.get_string('from_key'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('task_id')));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('vehicle_id')));
 end if;
 if kind='TARE_OFFER' then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',p_operation);
 elsif kind='TARE_ACCEPT' then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',v.get_string('offer_operation_id'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_ACCEPT',p_operation);end if;
 if kind!='TARE_OFFER' then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_JOURNAL',p_operation);end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
