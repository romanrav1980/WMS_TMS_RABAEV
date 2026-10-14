create or replace package body RRL_ST_DEFER_API as



 g_tx varchar2(100);



 function write_allowed return number is begin



  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;



 end;



 procedure scope(p_ware number,p_actor varchar2,p_right varchar2)is n number;begin



  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,p_right)=1



   and(u.WARE_ID=p_ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');



  if n!=1 or p_ware is null then raise_application_error(-20882,'ST_DEFER_CURRENT_WARE_ACTOR_REQUIRED');end if;



 end;



 procedure access_st(p_st varchar2,p_actor varchar2,p_right varchar2,p_ware out number)is n number;begin



  select count(distinct WARE_ID),min(WARE_ID)into n,p_ware from RRL_SBORKA_PALLETS where ST_NUMBER=p_st;



  if n!=1 then raise_application_error(-20886,'ST_DEFER_ONE_CURRENT_WARE_REQUIRED');end if;



  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=p_st and WARE_ID is null;



  if n>0 then raise_application_error(-20886,'ST_DEFER_NULL_WARE_REFUSED');end if;



  scope(p_ware,p_actor,p_right);



 end;



 procedure snapshot(p_st varchar2,p_actor varchar2,p_right varchar2,p_json out clob,p_hash out varchar2,p_ware out number,p_trip out number)is



  a json_array_t:=json_array_t();cargo json_array_t:=json_array_t();b json_object_t:=json_object_t();item json_object_t;v_count number:=0;v_cargo number:=0;v_trip_count number;v_ware_count number;



 begin



  select count(distinct WARE_ID),count(distinct nvl(TRANSTASK_ID,0)),min(WARE_ID),min(TRANSTASK_ID)



   into v_ware_count,v_trip_count,p_ware,p_trip from RRL_SBORKA_PALLETS where ST_NUMBER=p_st;



  if v_ware_count!=1 or v_trip_count!=1 or p_trip is null or p_trip<=0 then raise_application_error(-20886,'ST_DEFER_ONE_CURRENT_WARE_TRIP_REQUIRED');end if;



  access_st(p_st,p_actor,p_right,p_ware);



  for x in(select ID,PALLET_UID,WARE_ID,TRANSTASK_ID,CONDITION,ADDR,STDATE from RRL_SBORKA_PALLETS where ST_NUMBER=p_st order by ID fetch first 201 rows only)loop



   v_count:=v_count+1;if v_count>200 then raise_application_error(-20886,'ST_DEFER_MEMBER_BOUND_200');end if;



   item:=json_object_t();item.put('id',x.ID);item.put('pallet_identifier',x.PALLET_UID);item.put('warehouse_id',x.WARE_ID);



   item.put('trip_id',x.TRANSTASK_ID);item.put('condition',x.CONDITION);item.put('address',x.ADDR);item.put('st_date',to_char(x.STDATE,'YYYY-MM-DD HH24:MI:SS'));



   a.append(item);



  end loop;



  for x in(select r.ID,r.PALLET_UID,r.ARTICUL,r.EI,r.QUANTITY,r.PACK_COUNT,r.ORDER_WEIGHT,r.TAREWEIGHT,r.TARESIZE



   from RRL_SBORKA_PALLET_ROWS r join RRL_SBORKA_PALLETS p on p.PALLET_UID=r.PALLET_UID where p.ST_NUMBER=p_st



   order by r.PALLET_UID,r.ID fetch first 10001 rows only)loop



   v_cargo:=v_cargo+1;if v_cargo>10000 then raise_application_error(-20886,'ST_DEFER_CARGO_BOUND_10000');end if;



   item:=json_object_t();item.put('id',x.ID);item.put('pallet_identifier',x.PALLET_UID);item.put('articul',x.ARTICUL);item.put('unit_code',x.EI);



   item.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(x.QUANTITY));item.put('pack_count',RRL_STOCK_PLAN_HELPER.decimal_text(x.PACK_COUNT));



   item.put('weight',RRL_STOCK_PLAN_HELPER.decimal_text(x.ORDER_WEIGHT));item.put('pack_weight',RRL_STOCK_PLAN_HELPER.decimal_text(x.TAREWEIGHT));item.put('pack_size',RRL_STOCK_PLAN_HELPER.decimal_text(x.TARESIZE));



   cargo.append(item);



  end loop;



  b.put('cargo',cargo);



  b.put('st_number',p_st);b.put('warehouse_id',p_ware);b.put('source_trip_id',p_trip);b.put('members',a);



  for x in(select ID,CONDITION,TRANSPORT,SHIPMENT_DATE,SHIPMENT_TIME,DELETED,PAY_ORDER_ID from RRL_TRANSPORT_TASK where ID=p_trip)loop



   item:=json_object_t();item.put('id',x.ID);item.put('condition',x.CONDITION);item.put('vehicle',x.TRANSPORT);



   item.put('shipment_date',to_char(x.SHIPMENT_DATE,'YYYY-MM-DD'));item.put('shipment_time',to_char(x.SHIPMENT_TIME,'YYYY-MM-DD HH24:MI:SS'));



   item.put('deleted',x.DELETED);item.put('pay_order_id',x.PAY_ORDER_ID);b.put('source_trip',item);



  end loop;



  declare prepared json_object_t:=json_object_t.parse(RRL_ST_DEFER_PHYSICAL.snapshot(p_st,p_ware));begin if prepared.get_string('state')!='UNPICKED'then b.put('physical_preparation',prepared);end if;end;

  p_json:=b.to_clob;p_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_json,sys.dbms_crypto.hash_sh256)));



 end;



 procedure context(p_st varchar2,p_actor varchar2,p_result out clob)is



  src clob;hash varchar2(64);ware number;trip number;version_no number;b json_object_t;



 begin



  snapshot(p_st,p_actor,'transport_dispatch_view',src,hash,ware,trip);



  select nvl(max(VERSION_NO),0)into version_no from RRL_ST_DEFER_DECISION where ST_NUMBER=p_st;



  b:=json_object_t.parse(src);b.put('version',version_no);b.put('source_hash',hash);b.put('stock_changed',false);p_result:=b.to_clob;



 end;



 procedure history(p_st varchar2,p_actor varchar2,p_after number,p_result out clob)is



  ware number;a json_array_t:=json_array_t();b json_object_t:=json_object_t();item json_object_t;n number:=0;last_version number;more boolean:=false;



 begin



  access_st(p_st,p_actor,'transport_dispatch_view',ware);



  if p_after is null or p_after<0 or trunc(p_after)!=p_after then raise_application_error(-20886,'ST_DEFER_HISTORY_CURSOR_REQUIRED');end if;



  for x in(select VERSION_NO,RESULT_JSON from RRL_ST_DEFER_DECISION where ST_NUMBER=p_st and WARE_ID=ware and VERSION_NO>p_after order by VERSION_NO fetch first 51 rows only)loop



   n:=n+1;if n>50 then more:=true;exit;end if;



   item:=json_object_t.parse(x.RESULT_JSON);a.append(item);last_version:=x.VERSION_NO;



  end loop;



  b.put('st_number',p_st);b.put('warehouse_id',ware);b.put('rows',a);b.put('has_more',more);



  if more then b.put('next_after_version',last_version);else b.put_null('next_after_version');end if;



  b.put('stock_changed',false);p_result:=b.to_clob;



 end;



 procedure apply_decision(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob)is



  b json_object_t;src clob;hash varchar2(64);ware number;source_trip number;target_trip number;



  source_num varchar2(100);target_num varchar2(100);source_day date;target_day date;



  saved RRL_ST_DEFER_DECISION%rowtype;request_hash varchar2(64);version_no number;v_st varchar2(100);n number;



  v_meta boolean:=false;v_saved boolean:=false;answer varchar2(4000);assigned clob;sts json_array_t:=json_array_t();result json_object_t:=json_object_t();



 begin



  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_body is null or dbms_lob.getlength(p_body)>4000 then raise_application_error(-20886,'ST_DEFER_INPUT_BOUND');end if;



  b:=json_object_t.parse(p_body);v_st:=b.get_string('st_number');target_trip:=b.get_number('target_trip_id');



  if b.get_size!=6 or v_st is null or target_trip is null or target_trip<=0 or trunc(target_trip)!=target_trip



   or b.get_number('expected_version')is null or b.get_number('expected_version')<0 or trunc(b.get_number('expected_version'))!=b.get_number('expected_version')



   or b.get_string('source_hash')is null or b.get_string('reason')is null or length(trim(b.get_string('reason')))<8



   or b.get_string('reference')is null or length(trim(b.get_string('reference')))<8 then raise_application_error(-20886,'ST_DEFER_EXPLICIT_SOURCE_REASON_REQUIRED');end if;



  access_st(v_st,p_actor,'transport_dispatch_edit',ware);



  request_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));



  RRL_STOCK_METADATA_TX.begin_change(p_actor,'transport_dispatch_edit');v_meta:=true;savepoint RRL_ST_DEFER276;v_saved:=true;



  -- Current access is mandatory before replay; a saved replay does not regenerate physical facts.



  access_st(v_st,p_actor,'transport_dispatch_edit',ware);



  begin select *into saved from RRL_ST_DEFER_DECISION where OPERATION_ID=p_operation;



   if saved.ACTOR!=p_actor or saved.ST_NUMBER!=v_st or saved.REQUEST_HASH!=request_hash or dbms_lob.compare(saved.REQUEST_JSON,p_body)!=0 then raise_application_error(-20886,'ST_DEFER_OPERATION_PAYLOAD_CONFLICT');end if;



   scope(saved.WARE_ID,p_actor,'transport_dispatch_edit');p_result:=saved.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;



  exception when no_data_found then null;end;



  snapshot(v_st,p_actor,'transport_dispatch_edit',src,hash,ware,source_trip);



  if source_trip=target_trip then raise_application_error(-20886,'ST_DEFER_DIFFERENT_EXISTING_TRIP_REQUIRED');end if;



  select TRANSPORT,SHIPMENT_DATE into source_num,source_day from RRL_TRANSPORT_TASK where ID=source_trip;



  select TRANSPORT,SHIPMENT_DATE into target_num,target_day from RRL_TRANSPORT_TASK where ID=target_trip;



  for v in(select ID from RRL_TR_VEHICLE where NUM in(source_num,target_num)order by ID)loop



   select ID into n from RRL_TR_VEHICLE where ID=v.ID for update wait 3;



  end loop;



  for t in(select ID from RRL_TRANSPORT_TASK where ID in(source_trip,target_trip)order by ID)loop



   select ID into n from RRL_TRANSPORT_TASK where ID=t.ID for update wait 3;



   select count(*)into n from RRL_TRANSPORT_TASK where ID=t.ID and CONDITION='Спланирован'and nvl(DELETED,0)=0 and nvl(PAY_ORDER_ID,0)=0;



   if n!=1 then raise_application_error(-20886,'ST_DEFER_PLANNED_UNBILLED_TRIPS_REQUIRED');end if;



  end loop;



  select count(*)into n from RRL_TRANSPORT_TASK where (ID=source_trip and nvl(TRANSPORT,'~')!=nvl(source_num,'~'))or(ID=target_trip and nvl(TRANSPORT,'~')!=nvl(target_num,'~'));



  if n>0 then raise_application_error(-20886,'ST_DEFER_VEHICLE_CHANGED_RETRY');end if;



  select SHIPMENT_DATE into target_day from RRL_TRANSPORT_TASK where ID=target_trip;



  if target_day is null or source_day is null or trunc(target_day)<trunc(source_day)then raise_application_error(-20886,'ST_DEFER_TARGET_DAY_BEFORE_PROMISE');end if;



  n:=0;



  for x in(select ID from RRL_SBORKA_PALLETS where ST_NUMBER=v_st or TRANSTASK_ID=target_trip order by ID fetch first 401 rows only)loop



   n:=n+1;if n>400 then raise_application_error(-20886,'ST_DEFER_TOTAL_MEMBER_BOUND_400');end if;



   declare locked number;begin select ID into locked from RRL_SBORKA_PALLETS where ID=x.ID for update wait 3;end;



  end loop;



  snapshot(v_st,p_actor,'transport_dispatch_edit',src,hash,ware,source_trip);



  if hash!=b.get_string('source_hash')then raise_application_error(-20886,'ST_DEFER_SOURCE_CHANGED');end if;



  select nvl(max(VERSION_NO),0)into version_no from RRL_ST_DEFER_DECISION where ST_NUMBER=v_st;



  if version_no!=b.get_number('expected_version')then raise_application_error(-20886,'ST_DEFER_VERSION_CHANGED');end if;



  select count(*)into n from RRL_SBORKA_PALLETS p where p.ST_NUMBER=v_st and(



   nvl(p.CONDITION,0)=2 or exists(select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID where ls.SBORKA_PALLET_ID=p.ID and ls.ACTIVE_FLAG=1 and l.STATUS in('LOADED','DEPARTED'))



   or exists(select 1 from RRL_CASE_PICK_TASK c where c.LEGACY_SBORKA_PALLET_ID=p.ID)



   or exists(select 1 from RRL_CUSTOMER_ORDER_FULFILLMENT f where f.LEGACY_SBORKA_PALLET_ID=p.ID and f.PICKED_CASE_TASK_ID is not null));



  if n>0 then raise_application_error(-20886,'ST_DEFER_UNLOADED_SUPPORTED_PHYSICAL_SOURCE_ONLY');end if;



  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=v_st and STDATE is not null and trunc(STDATE)>trunc(target_day);



  if n>0 then raise_application_error(-20886,'ST_DEFER_TARGET_DAY_BEFORE_ST_PROMISE');end if;



  answer:=RRL_TT_ADD_PALL(0,v_st);



  if lower(substr(nvl(answer,'OK'),1,3))='err'then raise_application_error(-20886,'ST_DEFER_ORIGINAL_UNASSIGN_FAILED');end if;



  sts.append(v_st);RRL_TRANSPORT_PLAN_API.assign_sts(target_trip,sts.to_clob,p_actor,assigned);



  n:=RRL_TT_REORDER_ADR(source_trip);



  result.put('operation_id',p_operation);result.put('st_number',v_st);result.put('version',version_no+1);result.put('warehouse_id',ware);



  result.put('source_trip_id',source_trip);result.put('target_trip_id',target_trip);result.put('source_hash',hash);result.put('source',json_object_t.parse(src));



  result.put('original_shipping_date',to_char(source_day,'YYYY-MM-DD'));result.put('target_shipping_date',to_char(target_day,'YYYY-MM-DD'));



  result.put('reason',b.get_string('reason'));result.put('reference',b.get_string('reference'));result.put('actor',p_actor);



  if json_object_t.parse(src).has('physical_preparation')then result.put('physical_preparation',json_object_t.parse(src).get_object('physical_preparation'));end if;

  result.put('assignment',json_object_t.parse(assigned));result.put('stock_changed',false);result.put('original_demand_changed',false);result.put('operational_admission',false);



  p_result:=result.to_clob;g_tx:=dbms_transaction.local_transaction_id(false);



  insert into RRL_ST_DEFER_DECISION(OPERATION_ID,ST_NUMBER,VERSION_NO,SOURCE_TT_ID,TARGET_TT_ID,WARE_ID,ACTOR,REQUEST_HASH,REQUEST_JSON,SOURCE_HASH,SOURCE_JSON,RESULT_JSON)



   values(p_operation,v_st,version_no+1,source_trip,target_trip,ware,p_actor,request_hash,p_body,hash,src,p_result);



  g_tx:=null;RRL_STOCK_METADATA_TX.end_change;



 exception when others then



  g_tx:=null;if v_saved then rollback to RRL_ST_DEFER276;end if;



  if v_meta then RRL_STOCK_METADATA_TX.end_change;end if;raise;



 end;



end;




/
