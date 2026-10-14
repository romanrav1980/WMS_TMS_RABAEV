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
 procedure describe_command(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');s json_object_t:=d.get_object('source');kind varchar2(80):=d.get_string('command_type');
 v_owner number;v_type number;v_condition varchar2(10);v_from_kind varchar2(12);v_from_id varchar2(255);v_to_kind varchar2(12);v_to_id varchar2(255);
 v_from raw(32);v_to raw(32);v_from_qty number;v_from_version number;v_to_qty number;v_to_version number;v_qty number;v_tt number;v_vehicle number;v_store varchar2(255);v_reason varchar2(2000);v_ref varchar2(255);n number;v_offer_id varchar2(100);
 trip RRL_TRANSPORT_TASK%rowtype;vehicle RRL_TR_VEHICLE%rowtype;offer RRL_TARE_OFFER%rowtype;
 begin
 p_domain:=json_object_t();
 select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;if n!=1 then raise_application_error(-20882,'TARE_ACTIVE_ACTOR_REQUIRED');end if;
 if kind='TARE_COUNT' then
  if RRL_HAS_WRIGHT(p_actor,'tare_adjust')!=1 then raise_application_error(-20882,'TARE_ADJUSTMENT_PERMISSION_REQUIRED');end if;
  v_owner:=m.get_number('owner_ware_id');v_type:=m.get_number('pallet_type_id');v_condition:=m.get_string('condition');
  RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,v_owner);v_to_kind:='WAREHOUSE';v_to_id:=RRL_STOCK_PLAN_HELPER.decimal_text(v_owner);
  v_qty:=integer_qty(m.get_string('observed_quantity'),true);v_reason:=m.get_string('reason');v_ref:=m.get_string('decision_reference');
  if trim(v_reason) is null or lengthb(v_reason)>2000 or trim(v_ref) is null or lengthb(v_ref)>255 then raise_application_error(-20886,'TARE_ADJUSTMENT_REASON_DECISION_REQUIRED');end if;
 else
  if kind='TARE_ACCEPT' then
   v_offer_id:=s.get_string('offer_operation_id');select * into offer from RRL_TARE_OFFER where OPERATION_ID=v_offer_id;
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
  RRL_TARE_PARTICIPANT.holder_actor(p_actor,case when kind='TARE_ACCEPT' then v_to_kind else v_from_kind end,case when kind='TARE_ACCEPT' then v_to_id else v_from_id end,v_owner,trip,case when kind='TARE_ACCEPT' then 'tare_accept' else 'tare_offer' end);
  v_from:=RRL_TARE_BALANCE_KEY(v_owner,v_type,v_condition,v_from_kind,v_from_id);balance(v_from,v_from_qty,v_from_version);
  if v_from_qty<v_qty then raise_application_error(-20886,'TARE_SOURCE_QUANTITY_UNAVAILABLE');end if;
  p_domain.put('from_key',rawtohex(v_from));p_domain.put('from_kind',v_from_kind);p_domain.put('from_id',v_from_id);p_domain.put('from_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_from_qty));p_domain.put('from_version',v_from_version);
  p_domain.put('task_id',trip.ID);p_domain.put('vehicle_id',vehicle.ID);p_domain.put('vehicle_number',vehicle.NUM);p_domain.put('driver_id',trip.VODITEL_ID);p_domain.put('store_address',v_store);
 end if;
 if v_owner is null or v_type is null or v_condition is null or v_condition not in('GOOD','DAMAGED') or v_to_id is null or v_from_id is null and kind!='TARE_COUNT' then raise_application_error(-20886,'TARE_OWNER_TYPE_CONDITION_HOLDER_REQUIRED');end if;
 select count(*) into n from RRL_WARES where ID=v_owner;if n!=1 then raise_application_error(-20886,'TARE_OWNER_WAREHOUSE_REQUIRED');end if;
 select count(*) into n from RRL_PALLET_TYPE where PALLET_TYPE_ID=v_type and ACTIVE=1;if n!=1 then raise_application_error(-20886,'TARE_ACTIVE_EXISTING_PALLET_TYPE_REQUIRED');end if;
 v_to:=RRL_TARE_BALANCE_KEY(v_owner,v_type,v_condition,v_to_kind,v_to_id);balance(v_to,v_to_qty,v_to_version);
 if kind='TARE_COUNT' and v_qty<RRL_TARE_PLANNING.held_quantity(v_to) then raise_application_error(-20886,'TARE_COUNT_BELOW_ASSEMBLY_HOLD');end if;
 if kind in('TARE_OFFER','TARE_ACCEPT') and v_from_kind='WAREHOUSE' then RRL_TARE_PLANNING.assert_available(v_from,v_from_qty,v_qty);end if;
 if kind='TARE_COUNT' and(m.get_number('expected_version') is null or m.get_number('expected_version')!=v_to_version)then raise_application_error(-20886,'TARE_COUNT_VERSION_CONFLICT');end if;
 p_domain.put('owner_ware_id',v_owner);p_domain.put('pallet_type_id',v_type);p_domain.put('condition',v_condition);p_domain.put('to_key',rawtohex(v_to));p_domain.put('to_kind',v_to_kind);p_domain.put('to_id',v_to_id);
 p_domain.put('to_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_to_qty));p_domain.put('to_version',v_to_version);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
 if kind='TARE_COUNT' then p_domain.put('reason',v_reason);p_domain.put('decision_reference',v_ref);end if;
 if kind='TARE_ACCEPT' and v_to_kind='STORE' then
  declare policy_domain json_object_t;begin RRL_STOCK_TARE_POLICY.describe_store(v_to_id,policy_domain);p_domain.put('return_policy',policy_domain);end;
 end if;
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
 if kind='TARE_ACCEPT' and v.get_string('to_kind')='STORE' then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_DELIVERY_POLICY',p_operation);end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);kind varchar2(80):=d.get_string('command_type');op varchar2(100):=d.get_string('operation_id');
 v json_object_t;fresh json_object_t;plan clob;j json_object_t:=json_object_t();
 v_owner number;v_type number;v_condition varchar2(10);v_from raw(32);v_to raw(32);v_to_kind varchar2(12);v_to_id varchar2(255);v_from_kind varchar2(12);v_from_id varchar2(255);
 v_qty number;v_before number;v_after number;v_version number;v_reason varchar2(2000);v_ref varchar2(255);v_offer varchar2(100);v_offered number;v_tt number;v_vehicle number;v_vehicle_num varchar2(50);v_store varchar2(255);n number;
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
 if kind!='TARE_COUNT' then
  v_tt:=v.get_number('task_id');v_vehicle:=v.get_number('vehicle_id');
  select ID into n from RRL_TRANSPORT_TASK where ID=v_tt for update;
  select ID into n from RRL_TR_VEHICLE where ID=v_vehicle for update;
 end if;
 v_from:=hextoraw(v.get_string('from_key'));v_to:=hextoraw(v.get_string('to_key'));
 for row_record in(select BALANCE_KEY from RRL_TARE_BALANCE where BALANCE_KEY in(v_from,v_to)order by BALANCE_KEY for update)loop null;end loop;
 describe_command(p_request,p_actor,fresh);
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: tare context or quantity');end if;
 v_owner:=v.get_number('owner_ware_id');v_type:=v.get_number('pallet_type_id');v_condition:=v.get_string('condition');
 v_from:=hextoraw(v.get_string('from_key'));v_to:=hextoraw(v.get_string('to_key'));v_to_kind:=v.get_string('to_kind');v_to_id:=v.get_string('to_id');v_from_kind:=v.get_string('from_kind');v_from_id:=v.get_string('from_id');
 v_qty:=integer_qty(v.get_string('quantity'),kind='TARE_COUNT');v_before:=to_number(v.get_string('to_quantity'));v_version:=v.get_number('to_version');
 if kind='TARE_OFFER' then
  v_vehicle_num:=v.get_string('vehicle_number');v_store:=v.get_string('store_address');
  insert into RRL_TARE_OFFER(OPERATION_ID,FROM_BALANCE_KEY,TO_BALANCE_KEY,TT_ID,VEHICLE_ID,VEHICLE_NUMBER,STORE_ADDR,OWNER_WARE_ID,PALLET_TYPE_ID,CONDITION_CODE,FROM_KIND,FROM_ID,TO_KIND,TO_ID,QUANTITY,OFFERED_BY)
  values(op,v_from,v_to,v_tt,v_vehicle,v_vehicle_num,v_store,v_owner,v_type,v_condition,v_from_kind,v_from_id,v_to_kind,v_to_id,v_qty,p_actor);
  j.put('status','WAITING_OTHER_PARTICIPANT');j.put('tare_balance_changed',false);
 else
  if kind='TARE_ACCEPT' then
   v_offer:=v.get_string('offer_operation_id');v_offered:=to_number(v.get_string('offered_quantity'));
   insert into RRL_TARE_ACCEPT(OPERATION_ID,OFFER_OPERATION_ID,ACCEPTED_QTY,SHORT_QTY,ACCEPTED_BY)values(op,v_offer,v_qty,v_offered-v_qty,p_actor);
   if v_to_kind='STORE' then RRL_STOCK_TARE_POLICY.record_delivery(op,v.get_object('return_policy'));end if;
   update RRL_TARE_BALANCE set QUANTITY=QUANTITY-v_qty,BALANCE_VERSION=BALANCE_VERSION+1,LAST_OPERATION_ID=op,UPDATED_AT=systimestamp
    where BALANCE_KEY=v_from and QUANTITY>=v_qty;
   if sql%rowcount!=1 then raise_application_error(-20886,'TARE_SOURCE_QUANTITY_UNAVAILABLE');end if;
   v_after:=v_before+v_qty;
  else v_after:=v_qty;v_reason:=v.get_string('reason');v_ref:=v.get_string('decision_reference');end if;
  merge into RRL_TARE_BALANCE b using(select v_to BALANCE_KEY from dual)s on(b.BALANCE_KEY=s.BALANCE_KEY)
  when matched then update set QUANTITY=v_after,BALANCE_VERSION=BALANCE_VERSION+1,LAST_OPERATION_ID=op,UPDATED_AT=systimestamp
  when not matched then insert(BALANCE_KEY,OWNER_WARE_ID,PALLET_TYPE_ID,CONDITION_CODE,CUSTODIAN_KIND,CUSTODIAN_ID,QUANTITY,BALANCE_VERSION,LAST_OPERATION_ID)
  values(v_to,v_owner,v_type,v_condition,v_to_kind,v_to_id,v_after,1,op);
  insert into RRL_TARE_JOURNAL(OPERATION_ID,ACTION_KIND,FROM_BALANCE_KEY,TO_BALANCE_KEY,QUANTITY,BEFORE_QTY,AFTER_QTY,REASON_TEXT,DECISION_REFERENCE,ACTOR)
  values(op,case when kind='TARE_COUNT' then 'COUNT' else 'TRANSFER' end,v_from,v_to,case when kind='TARE_COUNT' then v_after-v_before else v_qty end,v_before,v_after,v_reason,v_ref,p_actor);
  j.put('status','POSTED');j.put('tare_balance_changed',true);j.put('destination_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_after));
  if kind='TARE_ACCEPT' then j.put('offer_operation_id',v_offer);j.put('short_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_offered-v_qty));end if;
 end if;
 j.put('operation_id',op);j.put('quantity',v.get_string('quantity'));j.put('owner_ware_id',v_owner);j.put('pallet_type_id',v_type);j.put('condition',v_condition);
 j.put('goods_stock_changed',false);p_result:=j.to_clob;
 end;
end;
/
