create or replace package RRL_STOCK_TARE_BOOK_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_TARE_BOOK_CMD as
 procedure describe_command(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);s json_object_t:=d.get_object('source');m json_object_t:=d.get_object('metadata');kind varchar2(80):=d.get_string('command_type');
 v_place_kind varchar2(6);v_place varchar2(200);v_type number;v_ware number;v_wave number;v_status varchar2(40);v_cell varchar2(60);v_content number;v_class varchar2(20);v_p number;v_available number;v_version number;v_key raw(32);n number;v_case number;v_book varchar2(100);
 booked RRL_TARE_BOOK%rowtype;pp RRL_PALLETS%rowtype;task RRL_CASE_PICK_TASK%rowtype;
 begin
 if RRL_HAS_WRIGHT(p_actor,'tare_plan')!=1 then raise_application_error(-20882,'TARE_ASSEMBLY_PLANNING_PERMISSION_REQUIRED');end if;
 if kind='TARE_BOOK_CANCEL' then
  v_book:=s.get_string('booking_operation_id');select * into booked from RRL_TARE_BOOK where OPERATION_ID=v_book and STATUS='HELD';
  v_place_kind:=booked.PLACE_KIND;v_place:=booked.PLACE_ID;v_type:=booked.PALLET_TYPE_ID;
 else v_place_kind:=s.get_string('place_kind');v_place:=s.get_string('place_id');v_type:=m.get_number('pallet_type_id');end if;
 if v_place_kind is null or v_place_kind not in('CASE','HU') or v_place is null then raise_application_error(-20886,'TARE_ASSEMBLY_EXISTING_PLACE_REQUIRED');end if;
 if v_place_kind='CASE' then
  if not regexp_like(v_place,'^[1-9][0-9]{0,18}$')then raise_application_error(-20886,'TARE_EXISTING_CASE_ID_REQUIRED');end if;
  v_case:=to_number(v_place);select * into task from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case;
  if v_type is not null and v_type!=task.PALLET_TYPE_ID then raise_application_error(-20886,'TARE_CASE_ORIGINAL_PALLET_TYPE_REQUIRED');end if;
  v_type:=task.PALLET_TYPE_ID;v_ware:=task.WARE_ID;v_wave:=task.PICK_WAVE_ID;v_status:=task.STATUS;
  select count(*) into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=v_case and ACTIVE_FLAG=1;
  if n!=0 then raise_application_error(-20886,'TARE_BOOK_TOP_PLACE_REQUIRED');end if;
  if kind='TARE_BOOK_CANCEL' then
   if task.STATUS not in('NEW','ASSIGNED','CANCELLED')then raise_application_error(-20886,'TARE_BOOK_CASE_PHYSICALLY_UNUSED_REQUIRED');end if;
   select count(*) into n from RRL_CASE_CARRIER_LOT l join RRL_REMAINS r on r.UID_POLETA=l.LOT_UID where l.CASE_PICK_TASK_ID=v_case and r.REMAIN>0;
   if n!=0 then raise_application_error(-20886,'TARE_BOOK_EMPTY_PLACE_REQUIRED');end if;
  elsif task.STATUS in('SHIPPED','CANCELLED')then raise_application_error(-20886,'TARE_CASE_ALREADY_DISPATCHED_OR_CANCELLED');end if;
 else
  select * into pp from RRL_PALLETS where UID_PALLET=v_place;
  if pp.HU_KIND!='CONTAINER' or pp.HU_CURRENT_CELL is null or pp.HU_TYPE not in('PALLET','ROLL_CAGE')then raise_application_error(-20886,'TARE_RETURNABLE_CURRENT_CONTAINER_REQUIRED');end if;
  v_cell:=pp.HU_CURRENT_CELL;v_content:=pp.HU_CONTENT_VERSION;v_status:=pp.HU_TYPE;
  select WARE_ID into v_ware from RRL_CELLS where CELL=v_cell;
  select LOAD_UNIT_CLASS into v_class from RRL_PALLET_TYPE where PALLET_TYPE_ID=v_type and ACTIVE=1;
  if(pp.HU_TYPE='PALLET' and v_class!='PALLET')or(pp.HU_TYPE='ROLL_CAGE' and v_class!='TROLLEY')then raise_application_error(-20886,'TARE_CONTAINER_PHYSICAL_TYPE_CONFLICT');end if;
  select count(*) into n from RRL_WMS_HU_LINK where CHILD_PALLET_UID=v_place and ACTIVE_FLAG=1;
  if n!=0 then raise_application_error(-20886,'TARE_BOOK_TOP_PLACE_REQUIRED');end if;
  select count(*) into n from RRL_TT_HU_LOAD_FACT where ROOT_UID=v_place and STATUS in('LOADED','DEPARTED');
  if n!=0 then raise_application_error(-20886,'TARE_BOOK_PLACE_ALREADY_ON_VEHICLE');end if;
  if kind='TARE_BOOK_CANCEL' then
   select count(*) into n from RRL_WMS_HU_LINK where PARENT_UID=v_place and ACTIVE_FLAG=1;
   if n!=0 then raise_application_error(-20886,'TARE_BOOK_EMPTY_PLACE_REQUIRED');end if;
  else
   select count(*) into n from RRL_TARE_BOOK b where b.STATUS='HELD' and(
    (b.PLACE_KIND='HU' and b.PLACE_ID in(select CHILD_PALLET_UID from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 start with PARENT_UID=v_place connect by nocycle prior CHILD_PALLET_UID=PARENT_UID and ACTIVE_FLAG=1))
    or(b.PLACE_KIND='CASE' and b.PLACE_ID in(select to_char(CHILD_CASE_TASK_ID,'TM9') from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 start with PARENT_UID=v_place connect by nocycle prior CHILD_PALLET_UID=PARENT_UID and ACTIVE_FLAG=1)));
   if n!=0 then raise_application_error(-20886,'TARE_NESTED_PLACE_ALREADY_BOOKED');end if;
  end if;
 end if;
 if m.has('expected_warehouse_id') and(m.get_number('expected_warehouse_id') is null or m.get_number('expected_warehouse_id')!=v_ware)then raise_application_error(-20886,'TARE_PLACE_SELECTED_WAREHOUSE_CONFLICT');end if;
 RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,v_ware);
 select count(*) into n from RRL_PALLET_TYPE where PALLET_TYPE_ID=v_type and ACTIVE=1;if n!=1 then raise_application_error(-20886,'TARE_ACTIVE_EXISTING_PALLET_TYPE_REQUIRED');end if;
 if kind='TARE_BOOK_CANCEL' and(booked.OWNER_WARE_ID!=v_ware or booked.PALLET_TYPE_ID!=v_type)then raise_application_error(-20886,'TARE_BOOK_ORIGINAL_WARE_TYPE_CONFLICT');end if;
 v_key:=RRL_TARE_BALANCE_KEY(v_ware,v_type,'GOOD','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(v_ware));
 select PHYSICAL_QTY,AVAILABLE_QTY,BALANCE_VERSION into v_p,v_available,v_version from RRL_TARE_AVAILABILITY where BALANCE_KEY=v_key;
 if kind='TARE_BOOK' then
  select count(*) into n from RRL_TARE_BOOK where PLACE_KIND=v_place_kind and PLACE_ID=v_place and STATUS='HELD';
  if n!=0 then raise_application_error(-20886,'TARE_PLACE_ALREADY_BOOKED');end if;
  if v_available<1 then raise_application_error(-20886,'TARE_GOOD_WAREHOUSE_AVAILABILITY_REQUIRED');end if;
 end if;
 p_domain:=json_object_t();p_domain.put('place_kind',v_place_kind);p_domain.put('place_id',v_place);p_domain.put('pallet_type_id',v_type);p_domain.put('warehouse_id',v_ware);p_domain.put('wave_id',v_wave);p_domain.put('place_status',v_status);p_domain.put('cell',v_cell);p_domain.put('content_version',v_content);
 p_domain.put('balance_key',rawtohex(v_key));p_domain.put('physical_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_p));p_domain.put('available_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_available));p_domain.put('balance_version',v_version);p_domain.put('booking_operation_id',v_book);
 exception when no_data_found then raise_application_error(-20886,'TARE_EXISTING_PLACE_OR_GOOD_COUNT_REQUIRED');end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
 describe_command(p_request,d.get_string('actor'),v);RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',v.get_string('balance_key'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',case when d.get_string('command_type')='TARE_BOOK_CANCEL' then v.get_string('booking_operation_id')else p_operation end);
 if v.get_string('place_kind')='CASE' then
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',v.get_string('place_id'));if v.get_number('wave_id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('wave_id')));end if;
 else RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',v.get_string('place_id'));RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v.get_string('place_id'));end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');kind varchar2(80):=d.get_string('command_type');plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_place varchar2(200);v_place_kind varchar2(6);v_key raw(32);v_ware number;v_type number;v_available number;v_book varchar2(100);n number;
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
 if v.get_number('wave_id') is not null then n:=v.get_number('wave_id');select PICK_WAVE_ID into n from RRL_PICK_WAVE where PICK_WAVE_ID=n for update;end if;
 v_place:=v.get_string('place_id');v_place_kind:=v.get_string('place_kind');
 if v_place_kind='CASE' then n:=to_number(v_place);select CASE_PICK_TASK_ID into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=n for update;
 else select HU_CONTENT_VERSION into n from RRL_PALLETS where UID_PALLET=v_place for update;end if;
 v_key:=hextoraw(v.get_string('balance_key'));select QUANTITY into n from RRL_TARE_BALANCE where BALANCE_KEY=v_key for update;
 describe_command(p_request,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: tare assembly');end if;
 v_ware:=v.get_number('warehouse_id');v_type:=v.get_number('pallet_type_id');v_available:=to_number(v.get_string('available_quantity'));v_book:=v.get_string('booking_operation_id');
 if kind='TARE_BOOK' then
 insert into RRL_TARE_BOOK(OPERATION_ID,BALANCE_KEY,OWNER_WARE_ID,PALLET_TYPE_ID,PLACE_KIND,PLACE_ID,CREATED_BY)values(op,v_key,v_ware,v_type,v_place_kind,v_place,p_actor);
 v_available:=v_available-1;
 else
 update RRL_TARE_BOOK set STATUS='CANCELLED',CLOSED_OPERATION_ID=op,CLOSED_BY=p_actor,CLOSED_AT=systimestamp where OPERATION_ID=v_book and STATUS='HELD';
 if sql%rowcount!=1 then raise_application_error(-20886,'TARE_BOOK_CURRENT_HOLD_REQUIRED');end if;v_available:=v_available+1;
 end if;
 update RRL_TARE_BALANCE set BALANCE_VERSION=BALANCE_VERSION+1,LAST_OPERATION_ID=op,UPDATED_AT=systimestamp where BALANCE_KEY=v_key;
 j.put('operation_id',op);j.put('status',case when kind='TARE_BOOK' then 'HELD' else 'CANCELLED' end);j.put('place_kind',v_place_kind);j.put('place_id',v_place);j.put('pallet_type_id',v_type);j.put('warehouse_id',v_ware);
 j.put('available_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_available));j.put('quantity','1');j.put('physical_tare_changed',false);j.put('goods_stock_changed',false);p_result:=j.to_clob;
 end;
end;
/
