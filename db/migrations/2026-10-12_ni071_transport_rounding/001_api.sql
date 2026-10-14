create or replace package RRL_TRANSPORT_COST_API authid definer as
 procedure preview(p_trip number,p_ware number,p_price number,p_actor varchar2,p_result out clob);
 procedure conduct(p_request clob,p_actor varchar2,p_result out clob);
 procedure assert_writing;
end;
/

create or replace package body RRL_TRANSPORT_COST_API as
 g_write boolean:=false;g_tx varchar2(100);
 procedure assert_writing is begin
  if not g_write or g_tx is null or g_tx!=dbms_transaction.local_transaction_id then
   raise_application_error(-20863,'TRANSPORT_COST_OWNER_REQUIRED');end if;
 end;
 procedure access_scope(p_ware number,p_actor varchar2,p_right varchar2)is n number;begin
  select count(*)into n from RUSERS u join RRL_WARES w on w.ID=p_ware where u.ID=p_actor and nvl(u.DELETED,0)=0
   and(u.WARE_ID=p_ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,p_right)=1;
  if n!=1 then raise_application_error(-20882,'TRANSPORT_COST_CURRENT_WAREHOUSE_RIGHT_REQUIRED');end if;
 end;
 procedure build(p_trip number,p_ware number,p_price number,p_actor varchar2,p_result out clob)is
  source_wire clob;norm_wire clob;s json_object_t;norm json_object_t;rate_source json_object_t;profile json_object_t;
  result json_object_t:=json_object_t();lines json_array_t:=json_array_t();missing json_array_t:=json_array_t();
  v_depart varchar2(100);v_instant varchar2(100);v_class varchar2(40);v_type varchar2(255);v_company varchar2(255);v_region varchar2(4000);
  basis_value varchar2(20);n number;dest_count number;received_count number;loads number;point_count number;
  v_vehicle number;v_vehicle_number varchar2(255);qty_roll number:=0;qty_pallet number:=0;qty_manual number:=0;qty_loader number:=0;
  total number:=0;rate_vehicle number;rate_point number;rate_roll number;rate_pallet number;rate_manual number;rate_loader number;
  procedure need(reason varchar2) is j json_object_t:=json_object_t();begin j.put('reason',reason);missing.append(j);end;
  procedure add_line(code varchar2,quantity number,rate_value number,line_basis varchar2)is j json_object_t:=json_object_t();amount number;begin
   if quantity=0 then return;end if;
   if rate_value is null or rate_value<0 or rate_value>=1e18 then raise_application_error(-20886,'TRANSPORT_RATE_INVALID');end if;
   amount:=round(quantity*rate_value,2);total:=total+amount;
   j.put('cost_code',code);j.put('quantity',quantity);j.put('rate',RRL_STOCK_PLAN_HELPER.decimal_text(rate_value));
   j.put('amount',RRL_STOCK_PLAN_HELPER.decimal_text(amount));j.put('basis',line_basis);lines.append(j);
  end;
 begin
  access_scope(p_ware,p_actor,'transport_dispatch_view');
  begin select vs.SOURCE_JSON into source_wire from RRL_TT_VEHICLE_SOURCE vs
   join RRL_STOCK_OPERATION o on o.OPERATION_ID=vs.DEPARTURE_OPERATION_ID and o.STATE='APPLIED'where vs.TT_ID=p_trip;
  exception when no_data_found then raise_application_error(-20886,'TRANSPORT_DEPARTURE_SOURCE_REQUIRED');end;
  s:=json_object_t.parse(source_wire);v_depart:=s.get_string('departure_operation_id');v_instant:=s.get_string('departed_at_instant');
  v_vehicle:=s.get_number('vehicle_id');v_vehicle_number:=s.get_string('vehicle_number');v_vehicle:=s.get_number('vehicle_id');v_vehicle_number:=s.get_string('vehicle_number');v_type:=s.get_string('task_vehicle_type');v_company:=s.get_string('carrier_company');v_region:=s.get_string('legacy_region_key');
  if s.get_string('profile_state')!='READY' then raise_application_error(-20886,'TRANSPORT_VEHICLE_PROFILE_REQUIRED');end if;
  profile:=s.get_object('vehicle_profile');profile:=profile.get_object('profile');v_class:=profile.get_string('vehicle_size_class');
  select count(*)into loads from RRL_TT_HU_LOAD_FACT where TT_ID=p_trip and DEPARTURE_OPERATION_ID=v_depart;
  if loads not between 1 and 200 then raise_application_error(-20886,'TRANSPORT_LOAD_BOUND');end if;
  select count(*)into n from RRL_TT_HU_LOAD_FACT l join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID and o.STATE='APPLIED'
   where l.TT_ID=p_trip and l.DEPARTURE_OPERATION_ID=v_depart and l.WARE_ID=p_ware
   and l.VEHICLE_ID=v_vehicle and l.VEHICLE_NUMBER=v_vehicle_number;
  if n!=loads then raise_application_error(-20886,'TRANSPORT_SINGLE_WAREHOUSE_SOURCE_REQUIRED');end if;
  select count(*),count(distinct DESTINATION_ADDR)into dest_count,point_count from(
   select distinct m.LOAD_OPERATION_ID,m.DESTINATION_ADDR from RRL_TT_HU_LOAD_ST m join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID
   where l.TT_ID=p_trip and l.DEPARTURE_OPERATION_ID=v_depart);
  if dest_count not between 1 and 200 then raise_application_error(-20886,'TRANSPORT_DESTINATION_BOUND');end if;
  select count(*)into n from RRL_TT_HU_LOAD_FACT l where l.TT_ID=p_trip and l.DEPARTURE_OPERATION_ID=v_depart and not exists(
   select 1 from RRL_TT_HU_LOAD_ST m where m.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID and m.DESTINATION_ADDR is not null);
  if n!=0 then raise_application_error(-20886,'TRANSPORT_DESTINATION_SOURCE_REQUIRED');end if;
  select count(*)into received_count from RRL_STORE_RECEIPT_FACT r
   join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.OPERATION_ID and o.STATE='APPLIED'
   join RRL_STORE_UNLOAD_FACT u on u.RECEIPT_OPERATION_ID=r.OPERATION_ID
   join RRL_STORE_UNLOAD_START us on us.OPERATION_ID=u.START_OPERATION_ID
   join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID
   where l.TT_ID=p_trip and l.DEPARTURE_OPERATION_ID=v_depart and exists(
    select 1 from RRL_TT_HU_LOAD_ST m where m.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID and m.DESTINATION_ADDR=r.STORE_ADDR);
  if received_count!=dest_count then need('ACTUAL_UNLOADING_REQUIRED');end if;
  begin select RESULT_JSON into norm_wire from RRL_TRANSPORT_NORM_HISTORY h
   where h.SOURCE_PRICE_ID=p_price and h.WARE_ID=p_ware
   and h.EFFECTIVE_FROM<=trunc(cast(to_timestamp_tz(v_instant,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')at time zone h.TIME_ZONE as date))
   order by h.EFFECTIVE_FROM desc,h.VERSION_NO desc fetch first 1 rows only;
  exception when no_data_found then raise_application_error(-20886,'TRANSPORT_NORM_PERIOD_REQUIRED');end;
  norm:=json_object_t.parse(norm_wire);rate_source:=norm.get_object('source');
  if norm.get_string('vehicle_type')!=v_type or norm.get_string('vehicle_size_class')!=v_class then raise_application_error(-20886,'TRANSPORT_NORM_VEHICLE_MISMATCH');end if;
  if rate_source.get_string('company')!='DEFAULT'and(v_company is null or rate_source.get_string('company')!=v_company)
   or rate_source.get_string('price_name')!='['||v_type||']'and(v_region is null or rate_source.get_string('price_name')!=v_region)
   then raise_application_error(-20886,'TRANSPORT_NORM_ROUTE_MISMATCH');end if;
  basis_value:=norm.get_string('unload_charge_basis');
  if basis_value is null or basis_value not in('POINT','PLACE')or not norm.has('pallet_unload_rate')then need('EXPLICIT_UNLOAD_NORM_REQUIRED');end if;
  rate_vehicle:=to_number(rate_source.get_string('vehicle_rate'),'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');
  rate_point:=to_number(rate_source.get_string('point_rate'),'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');
  rate_roll:=to_number(norm.get_string('rolling_unload_rate'),'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');
  rate_manual:=to_number(norm.get_string('manual_unload_rate'),'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');
  rate_loader:=to_number(norm.get_string('loader_rate'),'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');
  rate_pallet:=to_number(norm.get_string('pallet_unload_rate'),'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');
  for r in(
   select GROUP_KEY,min(METHOD)METHOD,count(distinct METHOD)METHOD_COUNT,max(EXTRA_LOADER)EXTRA_LOADER from(
    select case when basis_value='POINT'then r.STORE_ADDR else r.LOAD_OPERATION_ID||chr(1)||r.STORE_ADDR end GROUP_KEY,
     u.METHOD,case when u.METHOD='ROLL_CAGE'and u.ROLLING_DIFFICULT=1 and u.LOADER_PRESENT=1 then 1 else 0 end EXTRA_LOADER
    from RRL_STORE_RECEIPT_FACT r join RRL_STORE_UNLOAD_FACT u on u.RECEIPT_OPERATION_ID=r.OPERATION_ID
    join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.OPERATION_ID and o.STATE='APPLIED'
    join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID
    where l.TT_ID=p_trip and l.DEPARTURE_OPERATION_ID=v_depart and exists(
     select 1 from RRL_TT_HU_LOAD_ST m where m.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID and m.DESTINATION_ADDR=r.STORE_ADDR)
   )group by GROUP_KEY
  )loop
   if r.METHOD_COUNT!=1 then need('MIXED_METHOD_AT_POINT');
   elsif r.METHOD='PALLET'then qty_pallet:=qty_pallet+1;
   elsif r.METHOD='ROLL_CAGE'then qty_roll:=qty_roll+1;qty_loader:=qty_loader+r.EXTRA_LOADER;
   elsif r.METHOD='MANUAL'then qty_manual:=qty_manual+1;
   else need('UNSUPPORTED_UNLOAD_METHOD');end if;
  end loop;
  add_line('TRANSPORT_VEHICLE',1,rate_vehicle,'TRIP');add_line('TRANSPORT_POINT',point_count,rate_point,'POINT');
  if basis_value in('POINT','PLACE')then
   add_line('UNLOAD_PALLET',qty_pallet,rate_pallet,basis_value);add_line('UNLOAD_ROLL_CAGE',qty_roll,rate_roll,basis_value);
   add_line('UNLOAD_MANUAL',qty_manual,rate_manual,basis_value);add_line('UNLOAD_EXTRA_LOADER',qty_loader,rate_loader,basis_value);
  end if;
  result.put('trip_id',p_trip);result.put('warehouse_id',p_ware);result.put('currency',norm.get_string('currency'));
  result.put('departure',s);result.put('norm',norm);result.put('lines',lines);result.put('missing',missing);
  result.put('load_count',loads);result.put('destination_count',dest_count);result.put('complete',missing.get_size=0);
  if missing.get_size=0 then result.put('total',RRL_STOCK_PLAN_HELPER.decimal_text(total));else result.put_null('total');end if;
  result.put('amount_rounding','HALF_UP_2_PER_ARTICLE');result.put('cost_posted',false);result.put('stock_changed',false);
  result.put('carrier_invoice_changed',false);p_result:=result.to_clob;
 end;
 procedure preview(p_trip number,p_ware number,p_price number,p_actor varchar2,p_result out clob)is begin
  build(p_trip,p_ware,p_price,p_actor,p_result);
 end;
 procedure conduct(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);k json_key_list;op varchar2(100);trip number;ware number;price number;expected_norm_version number;currency_value varchar2(3);
  fingerprint raw(32);old_hash raw(32);old_result clob;wire clob;j json_object_t;norm json_object_t;s json_object_t;line json_object_t;
  arr json_array_t;v_depart varchar2(100);v_version number;v_currency varchar2(3);v_amount number;line_rate number;line_amount number;
  saved varchar2(100);payload clob;event_id varchar2(100);hash_values json_array_t:=json_array_t();hash_wire varchar2(4000);line_code varchar2(40);line_qty number;line_basis varchar2(20);
 begin
  savepoint transport_cost_conduct;
  k:=d.get_keys;if k.count!=6 then raise_application_error(-20886,'TRANSPORT_COST_EXACT_FIELDS_REQUIRED');end if;
  for i in 1..k.count loop if k(i)not in('operation_id','trip_id','warehouse_id','source_price_id','currency','expected_norm_version')then raise_application_error(-20886,'TRANSPORT_COST_UNKNOWN_FIELD');end if;end loop;
  op:=d.get_string('operation_id');trip:=d.get_number('trip_id');ware:=d.get_number('warehouse_id');price:=d.get_number('source_price_id');currency_value:=d.get_string('currency');expected_norm_version:=d.get_number('expected_norm_version');
  if op is null or lengthb(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')or expected_norm_version is null or expected_norm_version<1 or expected_norm_version!=trunc(expected_norm_version)or trip is null or ware is null or price is null or expected_norm_version is null or expected_norm_version<1 or expected_norm_version!=trunc(expected_norm_version)or trip is null or ware is null or price is null or trip<1 or ware<1 or price<1 or trip!=trunc(trip)or ware!=trunc(ware)or price!=trunc(price) or trip!=trunc(trip)or ware!=trunc(ware)or price!=trunc(price) or currency_value is null or not regexp_like(currency_value,'^[A-Z]{3}$')
   then raise_application_error(-20886,'TRANSPORT_COST_REQUEST_INVALID');end if;
  access_scope(ware,p_actor,'calc_tt_price');access_scope(ware,p_actor,'transport_dispatch_view');
  hash_values.append(trip);hash_values.append(ware);hash_values.append(price);hash_values.append(expected_norm_version);hash_values.append(currency_value);hash_values.append(p_actor);
  hash_wire:=hash_values.to_string;fingerprint:=dbms_crypto.hash(utl_i18n.string_to_raw(hash_wire,'AL32UTF8'),dbms_crypto.hash_sh256);
  select to_char(ID)into saved from RRL_TRANSPORT_TASK where ID=trip for update;
  begin select PAYLOAD_HASH,RESULT_JSON into old_hash,old_result from RRL_LOGISTICS_COST_RUN where OPERATION_ID=op;
   if old_hash!=fingerprint then raise_application_error(-20867,'TRANSPORT_COST_OPERATION_CONFLICT');end if;p_result:=old_result;return;
  exception when no_data_found then null;end;
  select to_char(VERSION_NO)into saved from RRL_TRANSPORT_NORM_HEAD where SOURCE_PRICE_ID=price and WARE_ID=ware for update;
  build(trip,ware,price,p_actor,wire);j:=json_object_t.parse(wire);
  if not j.get_boolean('complete')then raise_application_error(-20886,'TRANSPORT_COST_SOURCES_INCOMPLETE');end if;
  v_currency:=j.get_string('currency');if currency_value!=v_currency then raise_application_error(-20886,'TRANSPORT_COST_CURRENCY_MISMATCH');end if;
  s:=j.get_object('departure');v_depart:=s.get_string('departure_operation_id');norm:=j.get_object('norm');v_version:=norm.get_number('version');
  if v_version!=expected_norm_version then raise_application_error(-20867,'TRANSPORT_NORM_VERSION_CONFLICT');end if;
  j.put('operation_id',op);j.put('cost_posted',true);j.put('status','CALCULATED');j.put('calculated_by',p_actor);j.put('cost_kind','TRANSPORT_Q26');
  p_result:=j.to_clob;g_tx:=dbms_transaction.local_transaction_id(true);g_write:=true;
  insert into RRL_LOGISTICS_COST_RUN(OPERATION_ID,PAYLOAD_HASH,TT_ID,WARE_ID,CURRENCY,ACTOR,RESULT_JSON)values(op,fingerprint,trip,ware,v_currency,p_actor,p_result);
  insert into RRL_TRANSPORT_COST_CLAIM(DEPARTURE_OPERATION_ID,OPERATION_ID,SOURCE_PRICE_ID,VERSION_NO)values(v_depart,op,price,v_version);
  arr:=j.get_array('lines');
  for i in 0..arr.get_size-1 loop
   line:=treat(arr.get(i)as json_object_t);line_rate:=to_number(line.get_string('rate'),'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');
   line_amount:=to_number(line.get_string('amount'),'9999999999999999999999999D99','NLS_NUMERIC_CHARACTERS=''.,''');
   line_code:=line.get_string('cost_code');line_qty:=line.get_number('quantity');line_basis:=line.get_string('basis');
   line_code:=line.get_string('cost_code');line_qty:=line.get_number('quantity');line_basis:=line.get_string('basis');
   insert into RRL_TRANSPORT_COST_DETAIL(OPERATION_ID,COST_CODE,QUANTITY,RATE_VALUE,AMOUNT,BASIS)
    values(op,line_code,line_qty,line_rate,line_amount,line_basis);
  end loop;
  event_id:='FIN:'||rawtohex(dbms_crypto.hash(utl_i18n.string_to_raw('TRANSPORT_COST_RECOGNIZED:'||op,'AL32UTF8'),dbms_crypto.hash_sh256));
  j.put('event_type','TRANSPORT_COST_RECOGNIZED');j.put('posting_semantics','MONETARY_RECOGNITION');j.put('external_sap_ack',false);payload:=j.to_clob;
  insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values(event_id,'TRANSPORT_COST_RECOGNIZED',payload);
  g_write:=false;g_tx:=null;
 exception when others then g_write:=false;g_tx:=null;rollback to transport_cost_conduct;raise;
 end;
end;
/
