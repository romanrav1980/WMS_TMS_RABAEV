create or replace package body RRL_TT_OPERATION_PLAN_API as
 procedure store_fact(p_operation number,p_start date,p_finish date,p_note varchar2)is
 begin
  if p_start is not null and p_finish is not null and p_finish<p_start then raise_application_error(-20886,'OP_FACT_FINISH_BEFORE_START');end if;
  update RRL_TT_OPERATIONS set FACT_START=p_start,FACT_END=p_finish,NOTE=p_note where ID=p_operation;
 end;
 procedure assert_driver(p_driver number,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_TRANSPORT_DRIVER_USER b join RUSERS u on u.ID=b.USER_ID
   join RRL_TR_VODITEL d on d.ID=b.DRIVER_ID
   where b.DRIVER_ID=p_driver and b.USER_ID=p_actor and b.ACTIVE=1 and nvl(u.DELETED,0)=0 and nvl(d.DELETED,0)=0 and RRL_DRIVER_SCOPE.allowed_account(u.ID,b.DRIVER_ID)=1;
  if n!=1 then raise_application_error(-20882,'DRIVER_CURRENT_ACCOUNT_BINDING_REQUIRED');end if;
 end;
 procedure actor_allowed(p_actor varchar2)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1;
  if n!=1 then raise_application_error(-20882,'OP_PLAN_ACTIVE_DISPATCHER_REQUIRED');end if;
 end;
 procedure generate(p_trip number,p_actor varchar2,p_result out clob)is
  w RRL_TRANSPORT_TASK%rowtype;before_plate varchar2(50);v_vehicle number;v_locked number;
  v_route_drive number;v_route_back number;v_route_basis varchar2(50);
  v_count number:=0;v_global number;v_places number;v_time date;v_finish date;v_id number;
  chain json_array_t:=json_array_t.parse('["DOCK_ASSIGN","WAIT_LOAD","LOADING","CLOSE_GATE","DOCUMENTS","DEPART","DRIVE","UNLOAD","LOAD_RETURNS","DRIVE_BACK","RETURN_HANDOVER","CLEAN_RETURNS"]');
  chain_text clob;norms_text clob;norms json_array_t;norm_map json_object_t:=json_object_t();norm json_object_t;
  v_code varchar2(50);v_note RRL_TT_OPERATIONS.NOTE%type;v_duration number;v_per number;v_ordinal number;v_rows number;v_checks clob;
  sts json_array_t:=json_array_t();seen json_object_t:=json_object_t();result json_array_t:=json_array_t();item json_object_t;
 begin
  savepoint RRL_OP_PLAN141;actor_allowed(p_actor);
  select TRANSPORT into before_plate from RRL_TRANSPORT_TASK where ID=p_trip;
  if before_plate is not null then
   begin select ID into v_vehicle from RRL_TR_VEHICLE where NUM=before_plate;
    select ID into v_locked from RRL_TR_VEHICLE where ID=v_vehicle for update;
   exception when no_data_found then raise_application_error(-20886,'OP_PLAN_CURRENT_VEHICLE_REQUIRED');end;
  end if;
  select *into w from RRL_TRANSPORT_TASK where ID=p_trip for update;
  if nvl(w.TRANSPORT,'~')!=nvl(before_plate,'~')then raise_application_error(-20886,'OP_PLAN_VEHICLE_CHANGED_RETRY');end if;
  if nvl(w.DELETED,0)!=0 or w.CONDITION='Отгружен'or nvl(w.PAY_ORDER_ID,0)>0 then raise_application_error(-20886,'OP_PLAN_ACTIVE_UNBILLED_TRIP_REQUIRED');end if;
  select count(*)into v_count from RRL_TT_HU_LOAD_FACT where TT_ID=p_trip and STATUS in('LOADED','DEPARTED');
  if v_count>0 then raise_application_error(-20886,'OP_PLAN_PHYSICAL_TRIP_FROZEN');end if;
  v_count:=0;
  for source in(select ID,ST_NUMBER,WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip order by ID fetch first 201 rows only)loop
   v_count:=v_count+1;if v_count>200 then raise_application_error(-20886,'OP_PLAN_SOURCE_BOUND_200');end if;
   if source.ST_NUMBER is null then raise_application_error(-20886,'OP_PLAN_SOURCE_ID_REQUIRED');end if;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,source.WARE_ID);
   if not seen.has(source.ST_NUMBER)then seen.put(source.ST_NUMBER,true);sts.append(source.ST_NUMBER);end if;
  end loop;
  if v_count=0 and nvl(w.USER_ID,'~')!=p_actor then
   select count(*)into v_global from RUSERS where ID=p_actor and upper(trim(USER_GROUP))='GLOBAL_ADMIN';
   if v_global!=1 then raise_application_error(-20882,'OP_PLAN_EMPTY_TRIP_OWNER_REQUIRED');end if;
  end if;
  RRL_TRANSPORT_PLAN_RULES.check_vehicle(v_vehicle,sts.to_clob,0,v_checks);
  if w.SHIPMENT_DATE is null or w.SHIPMENT_TIME is null then raise_application_error(-20886,'OP_PLAN_EXPLICIT_TRIP_DATE_TIME_REQUIRED');end if;
  v_time:=trunc(w.SHIPMENT_DATE)+(w.SHIPMENT_TIME-trunc(w.SHIPMENT_TIME));
  select count(distinct PALLET_UID)into v_places from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip;
  for old in(select ID,FACT_START,FACT_END from RRL_TT_OPERATIONS where TT_ID=p_trip order by ID for update)loop
   if old.FACT_START is not null or old.FACT_END is not null then raise_application_error(-20886,'OP_PLAN_EXECUTION_HISTORY_FROZEN');end if;
  end loop;
  chain_text:=chain.to_clob;
  select count(*)into v_count from RRL_TT_OPERATIONS where TT_ID=p_trip and OPERATION_CODE not in(select CODE from json_table(chain_text,'$[*]'columns(CODE varchar2(50)path '$')));
  if v_count>0 then raise_application_error(-20886,'OP_PLAN_CUSTOM_CHAIN_REVIEW_REQUIRED');end if;
  select count(*)into v_count from(select OPERATION_CODE from RRL_TT_OPERATIONS where TT_ID=p_trip group by OPERATION_CODE having count(*)>1);
  if v_count>0 then raise_application_error(-20886,'OP_PLAN_DUPLICATE_CHAIN_REVIEW_REQUIRED');end if;
  -- One statement snapshot for all configured norms. Explicit configured zero is preserved.
  select json_arrayagg(json_object('code' value OPERATION_CODE,'duration' value DURATION_MIN,'per' value PER_UNIT)order by OPERATION_CODE returning clob)
   into norms_text from RRL_TRANSPORT_NORMS where OPERATION_CODE in(select CODE from json_table(chain_text,'$[*]'columns(CODE varchar2(50)path '$')));
  if norms_text is null then raise_application_error(-20886,'OP_PLAN_NORMS_REQUIRED');end if;
  norms:=json_array_t.parse(norms_text);
  for i in 0..norms.get_size-1 loop norm:=treat(norms.get(i)as json_object_t);
   if norm_map.has(norm.get_string('code'))then raise_application_error(-20886,'OP_PLAN_NORM_DUPLICATE');end if;
   norm_map.put(norm.get_string('code'),norm);
  end loop;
  RRL_TT_ROUTE_SOURCE.durations(p_trip,p_actor,v_route_drive,v_route_back,v_route_basis);
  for i in 0..chain.get_size-1 loop
   v_code:=chain.get_string(i);v_ordinal:=i+1;
   if not norm_map.has(v_code)then raise_application_error(-20886,'OP_PLAN_NORM_MISSING:'||v_code);end if;
   norm:=norm_map.get_object(v_code);v_duration:=norm.get_number('duration');v_per:=norm.get_number('per');
   if v_duration is null or v_duration<0 or v_per is null or v_per not in(0,1)then raise_application_error(-20886,'OP_PLAN_NORM_INVALID:'||v_code);end if;
   if v_per=1 then v_duration:=v_duration*v_places;end if;
   if v_code='DRIVE'and v_route_drive is not null then v_duration:=v_route_drive;end if;
   if v_code='DRIVE_BACK'and v_route_back is not null then v_duration:=v_route_back;end if;
   v_finish:=v_time+round(v_duration*60)/86400;
   begin select ID into v_id from RRL_TT_OPERATIONS where TT_ID=p_trip and OPERATION_CODE=v_code;
    update RRL_TT_OPERATIONS set ORD=v_ordinal,DURATION_MIN=v_duration,PLAN_START=v_time,PLAN_END=v_finish where ID=v_id;
   exception when no_data_found then
    select SEQ_TT_OPERATIONS.nextval into v_id from dual;
    insert into RRL_TT_OPERATIONS(ID,TT_ID,OPERATION_CODE,ORD,DURATION_MIN,PLAN_START,PLAN_END)values(v_id,p_trip,v_code,v_ordinal,v_duration,v_time,v_finish);
   end;
   item:=json_object_t();item.put('op_id',v_id);item.put('tt_id',p_trip);item.put('operation_code',v_code);item.put('ord',v_ordinal);
   item.put('duration_min',v_duration);item.put('plan_start',to_char(v_time,'YYYY-MM-DD HH24:MI'));item.put('plan_end',to_char(v_finish,'YYYY-MM-DD HH24:MI'));
   item.put_null('fact_start');item.put_null('fact_end');item.put_null('delta_min');
   select NOTE into v_note from RRL_TT_OPERATIONS where ID=v_id;item.put('note',v_note);
   if v_code in('DRIVE','DRIVE_BACK')then item.put('planning_basis',v_route_basis);else item.put('planning_basis','CONFIGURED_NORMS_ESTIMATE');end if;item.put('time_window_admission',false);
   result.append(item);v_time:=v_finish;
  end loop;
  p_result:=result.to_clob;
 exception when others then rollback to RRL_OP_PLAN141;raise;
 end;
 procedure write_fact(p_operation number,p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t:=json_object_t.parse(p_body);before_trip number;w RRL_TRANSPORT_TASK%rowtype;o RRL_TT_OPERATIONS%rowtype;
  v_start date;v_finish date;v_note RRL_TT_OPERATIONS.NOTE%type;n number:=0;v_global number;result json_object_t:=json_object_t();
 begin
  savepoint RRL_OP_FACT141;actor_allowed(p_actor);
  select TT_ID into before_trip from RRL_TT_OPERATIONS where ID=p_operation;
  select *into w from RRL_TRANSPORT_TASK where ID=before_trip for update;
  if nvl(w.DELETED,0)!=0 then raise_application_error(-20886,'OP_FACT_ACTIVE_TRIP_REQUIRED');end if;
  for source in(select ID,WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=before_trip order by ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'OP_FACT_SOURCE_BOUND_200');end if;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,source.WARE_ID);
  end loop;
  if n=0 and nvl(w.USER_ID,'~')!=p_actor then
   select count(*)into v_global from RUSERS where ID=p_actor and upper(trim(USER_GROUP))='GLOBAL_ADMIN';
   if v_global!=1 then raise_application_error(-20882,'OP_FACT_EMPTY_TRIP_OWNER_REQUIRED');end if;
  end if;
  select *into o from RRL_TT_OPERATIONS where ID=p_operation for update;
  if o.TT_ID!=before_trip then raise_application_error(-20886,'OP_FACT_SOURCE_CHANGED_RETRY');end if;
  v_start:=o.FACT_START;v_finish:=o.FACT_END;v_note:=o.NOTE;
  if b.has('fact_start')then v_start:=to_date(b.get_string('fact_start'),'FXYYYY-MM-DD HH24:MI');end if;
  if b.has('fact_end')then v_finish:=to_date(b.get_string('fact_end'),'FXYYYY-MM-DD HH24:MI');end if;
  if v_start is not null and v_finish is not null and v_finish<v_start then raise_application_error(-20886,'OP_FACT_FINISH_BEFORE_START');end if;
  if b.has('note')then v_note:=b.get_string('note');end if;
  store_fact(p_operation,v_start,v_finish,v_note);
  result.put('op_id',p_operation);result.put('updated',true);p_result:=result.to_clob;
 exception when others then rollback to RRL_OP_FACT141;raise;
 end;
 procedure mark_driver_fact(p_operation number,p_driver number,p_actor varchar2,p_action varchar2,p_result out clob)is
  before_trip number;b_user varchar2(50);b_active number;w RRL_TRANSPORT_TASK%rowtype;o RRL_TT_OPERATIONS%rowtype;
  v_now date:=sysdate;v_start date;v_finish date;changed boolean:=false;result json_object_t:=json_object_t();
 begin
  savepoint RRL_DRIVER_FACT1302;
  lock table RRL_ACCESS_REV in share mode wait 5;
  if p_action is null or p_action not in('START','DONE')then raise_application_error(-20886,'DRIVER_FACT_ACTION_INVALID');end if;
  assert_driver(p_driver,p_actor);
  select USER_ID,ACTIVE into b_user,b_active from RRL_TRANSPORT_DRIVER_USER where DRIVER_ID=p_driver for update nowait;
  assert_driver(p_driver,p_actor);
  select TT_ID into before_trip from RRL_TT_OPERATIONS where ID=p_operation;
  select *into w from RRL_TRANSPORT_TASK where ID=before_trip for update nowait;
  if w.VODITEL_ID is null or w.VODITEL_ID!=p_driver or nvl(w.DELETED,0)!=0 then raise_application_error(-20882,'DRIVER_TRIP_ASSIGNMENT_REQUIRED');end if;
  if nvl(w.PAY_ORDER_ID,0)>0 then raise_application_error(-20886,'DRIVER_INVOICED_TRIP_FROZEN');end if;
  select *into o from RRL_TT_OPERATIONS where ID=p_operation for update nowait;
  if o.TT_ID!=before_trip then raise_application_error(-20886,'DRIVER_OPERATION_TRIP_CHANGED');end if;
  v_start:=o.FACT_START;v_finish:=o.FACT_END;
  if p_action='START'and v_start is null then
   if v_finish is not null then raise_application_error(-20886,'DRIVER_FACT_STATE_CONFLICT');end if;
   v_start:=v_now;changed:=true;
  elsif p_action='DONE'and v_finish is null then
   if v_start is null then raise_application_error(-20886,'DRIVER_FACT_START_REQUIRED');end if;
   v_finish:=v_now;changed:=true;
  end if;
  assert_driver(p_driver,p_actor);
  if changed then store_fact(p_operation,v_start,v_finish,o.NOTE);end if;
  result.put('op_id',p_operation);result.put('trip_id',before_trip);result.put('driver_id',p_driver);
  if v_finish is not null then result.put('status','done');elsif v_start is not null then result.put('status','in_progress');else result.put('status','pending');end if;
  result.put('fact_start',to_char(v_start,'YYYY-MM-DD HH24:MI:SS'));result.put('fact_end',to_char(v_finish,'YYYY-MM-DD HH24:MI:SS'));
  result.put('changed',changed);result.put('clock_basis','EXISTING_DATABASE_LOCAL_DATE');
  result.put('stock_changed',false);p_result:=result.to_clob;
 exception when others then rollback to RRL_DRIVER_FACT1302;raise;
 end;
end;
/
