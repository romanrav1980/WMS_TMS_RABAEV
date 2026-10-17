create or replace package body RRL_STOCK_STORE_WEIGHT_CORE as
 procedure resolve_weight(p_source clob,p_metadata clob,p_actor varchar2,p_proof out json_object_t,p_has_issue out boolean) is
  src json_object_t:=json_object_t.parse(p_source);m json_object_t:=json_object_t.parse(p_metadata);cap RRL_STORE_SCALE_CAPTURE%rowtype;device RRL_STORE_SCALE_DEVICE%rowtype;
  photos json_array_t;ids json_array_t:=json_array_t();v_key varchar2(64);v_load varchar2(100):=src.get_string('load_operation_id');v_store varchar2(255):=src.get_string('store_address');
  v_photo varchar2(64);v_view varchar2(12);v_sha varchar2(64);v_ship number;v_actual number;v_min number;v_tol number;v_delta number;v_count number;v_in_range number;v_act number:=0;reason_text varchar2(32767);
  type seen_map is table of number index by varchar2(64);seen seen_map;v_views seen_map;assets_seen seen_map;view_count number:=0;item json_object_t;
 begin
  p_proof:=null;p_has_issue:=false;
  if src.get_string('mode')in('BARCODE','PAPER_COUNT')then
   if m.has('manual_weight_kg')and not m.get('manual_weight_kg').is_null then raise_application_error(-20886,'STORE_MANUAL_WEIGHT_REQUIRES_WEIGHT_STRATEGY');end if;
   return;end if;
  if src.get_string('mode') is null or src.get_string('mode')!='WEIGHT_PHOTO' then raise_application_error(-20886,'STORE_RECEIPT_MODE_UNSUPPORTED');end if;
  v_key:=m.get_string('scale_capture_key');
  if m.has('manual_weight_kg')and not m.get('manual_weight_kg').is_null then
   if v_key is not null then raise_application_error(-20886,'STORE_WEIGHT_SINGLE_SOURCE_REQUIRED');end if;
   if p_actor is null or not m.get('manual_weight_kg').is_string
    or not regexp_like(m.get_string('manual_weight_kg'),'^[0-9]{1,18}(\.[0-9]{1,9})?$')then
    raise_application_error(-20886,'STORE_MANUAL_GROSS_KG_REQUIRED');end if;
   v_actual:=RRL_STOCK_MATH.quantity(m.get_string('manual_weight_kg'));
   if v_actual<=0 then raise_application_error(-20886,'STORE_MANUAL_POSITIVE_GROSS_REQUIRED');end if;
  else
  if v_key is null then raise_application_error(-20886,'STORE_RECEIPT_WEIGHT_AND_PHOTOS_REQUIRED');end if;
  select * into cap from RRL_STORE_SCALE_CAPTURE where CAPTURE_KEY=v_key;
  if cap.LOAD_OPERATION_ID!=v_load or cap.STORE_ADDR!=v_store then raise_application_error(-20886,'STORE_WEIGHT_CAPTURE_SOURCE_MISMATCH');end if;
  select * into device from RRL_STORE_SCALE_DEVICE where DEVICE_ID=cap.DEVICE_ID;
  if RRL_HAS_WRIGHT(device.SENDER_ID,'store_scale_ingest')!=1 or device.SENDER_ID!=cap.RECORDED_BY or device.ACTIVE_FLAG!=1 or device.POLICY_VERSION!=cap.DEVICE_POLICY_VERSION or device.STORE_ADDR!=v_store or device.CALIBRATED_UNTIL<systimestamp
   or cap.RECEIVED_AT<systimestamp-numtodsinterval(300,'SECOND') or cap.MEASURED_AT<systimestamp-numtodsinterval(300,'SECOND') then raise_application_error(-20886,'STORE_WEIGHT_CAPTURE_EXPIRED_OR_POLICY_CHANGED');end if;
   v_actual:=cap.GROSS_WEIGHT_KG;
  end if;
  select count(*)into v_count from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=v_load and COVERAGE_COMPLETE!=1;
  if v_count>0 then raise_application_error(-20886,'STORE_WEIGHT_COMPLETE_FROZEN_BOXES_REQUIRED');end if;
  select count(*),min(GROSS_WEIGHT_KG) into v_count,v_min from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=v_load;
  if v_count<1 or v_count>200 or v_min is null or v_min<=0 then raise_application_error(-20886,'STORE_WEIGHT_FROZEN_PHYSICAL_BOXES_REQUIRED');end if;
  v_ship:=RRL_STOCK_MATH.quantity(src.get_string('shipping_gross_weight_kg'));v_tol:=v_min/2;v_delta:=v_actual-v_ship;
  if not m.has('photo_ids') or not m.get('photo_ids').is_array then raise_application_error(-20886,'STORE_WEIGHT_PHOTOS_REQUIRED');end if;photos:=m.get_array('photo_ids');
  if photos.get_size<3 or photos.get_size>12 then raise_application_error(-20881,'STORE_WEIGHT_PHOTO_BOUND_3_12');end if;
  for i in 0..photos.get_size-1 loop
   v_photo:=photos.get_string(i);
   if v_photo is null or seen.exists(v_photo) then raise_application_error(-20886,'STORE_WEIGHT_PHOTO_DUPLICATE');end if;seen(v_photo):=1;
   select VIEW_CODE,ASSET_SHA256 into v_view,v_sha from RRL_STORE_RECEIPT_PHOTO where PHOTO_ID=v_photo and LOAD_OPERATION_ID=v_load and STORE_ADDR=v_store;
   if assets_seen.exists(v_sha) then raise_application_error(-20886,'STORE_WEIGHT_DISTINCT_ORIGINAL_PHOTOS_REQUIRED');end if;assets_seen(v_sha):=1;
   if not v_views.exists(v_view) then v_views(v_view):=1;view_count:=view_count+1;end if;
   item:=json_object_t();item.put('photo_id',v_photo);item.put('view',v_view);item.put('sha256',v_sha);ids.append(item);
  end loop;
  if view_count<3 then raise_application_error(-20886,'STORE_WEIGHT_THREE_DISTINCT_VIEWS_REQUIRED');end if;
  v_in_range:=case when abs(v_delta)<=v_tol then 1 else 0 end;
  if v_in_range=0 then
   if not m.has('weight_act_confirmed') then raise_application_error(-20886,'STORE_WEIGHT_ACT_REQUIRED');end if;
   if m.get_boolean('weight_act_confirmed') then null;else raise_application_error(-20886,'STORE_WEIGHT_ACT_REQUIRED');end if;
   if RRL_HAS_WRIGHT(p_actor,'store_weight_act')!=1 then raise_application_error(-20882,'STORE_WEIGHT_REPRESENTATIVE_REQUIRED');end if;
   reason_text:=m.get_string('case_note');
   if trim(reason_text) is null or lengthb(reason_text)>2000 or not m.has('observations') then raise_application_error(-20886,'STORE_WEIGHT_ACT_COUNTS_AND_REASON_REQUIRED');end if;
   if m.get_array('observations').get_size=0 then raise_application_error(-20886,'STORE_WEIGHT_ACT_COUNTS_AND_REASON_REQUIRED');end if;
   v_act:=1;p_has_issue:=true;
  end if;
  p_proof:=json_object_t();p_proof.put('capture_key',v_key);p_proof.put('device_id',cap.DEVICE_ID);p_proof.put('device_policy_version',cap.DEVICE_POLICY_VERSION);
  if v_key is null then p_proof.put('measurement_origin','MANUAL_CONFIRMED');p_proof.put('recorded_by',p_actor);end if;
  p_proof.put('shipping_gross_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_ship));p_proof.put('observed_gross_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_actual));
  p_proof.put('tolerance_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_tol));p_proof.put('delta_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_delta));p_proof.put('in_tolerance',v_in_range);p_proof.put('act_confirmed',v_act);p_proof.put('photos',ids);
 exception when no_data_found then raise_application_error(-20886,'STORE_WEIGHT_CAPTURE_OR_PHOTO_SOURCE_NOT_FOUND');
 end;
 procedure declare_rows(p_operation varchar2,p_proof json_object_t,r in out nocopy json_array_t) is photos json_array_t;x json_object_t;
 begin
  if p_proof is null then return;end if;
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_WEIGHT',p_operation);photos:=p_proof.get_array('photos');
  for i in 0..photos.get_size-1 loop x:=treat(photos.get(i) as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_WEIGHT_PHOTO',p_operation||':'||x.get_string('photo_id'));end loop;
 end;
 procedure persist(p_operation varchar2,p_proof json_object_t,p_actor varchar2) is
  v_key varchar2(64);v_ship number;v_actual number;v_tol number;v_delta number;v_in_range number;v_act number;v_photos clob;photos json_array_t;x json_object_t;v_photo varchar2(64);
 begin
  if p_proof is null then return;end if;
  v_key:=p_proof.get_string('capture_key');v_ship:=RRL_STOCK_MATH.quantity(p_proof.get_string('shipping_gross_kg'));v_actual:=RRL_STOCK_MATH.quantity(p_proof.get_string('observed_gross_kg'));v_tol:=p_proof.get_number('tolerance_kg');v_delta:=v_actual-v_ship;v_in_range:=p_proof.get_number('in_tolerance');v_act:=p_proof.get_number('act_confirmed');photos:=p_proof.get_array('photos');v_photos:=photos.to_clob;
  insert into RRL_STORE_RECEIPT_WEIGHT(OPERATION_ID,CAPTURE_KEY,SHIPPING_GROSS_KG,OBSERVED_GROSS_KG,TOLERANCE_KG,DELTA_KG,IN_TOLERANCE,ACT_CONFIRMED,PHOTOS_JSON,RECORDED_BY,MEASUREMENT_ORIGIN)
   values(p_operation,v_key,v_ship,v_actual,v_tol,v_delta,v_in_range,v_act,v_photos,p_actor,nvl(p_proof.get_string('measurement_origin'),'SCALE_CAPTURE'));
  for i in 0..photos.get_size-1 loop x:=treat(photos.get(i) as json_object_t);v_photo:=x.get_string('photo_id');
   insert into RRL_STORE_RECEIPT_WEIGHT_PHOTO(OPERATION_ID,PHOTO_ID)values(p_operation,v_photo);
  end loop;
 end;
end;
/
