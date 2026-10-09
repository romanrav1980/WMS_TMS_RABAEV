create or replace package RRL_STOCK_WAVE_LAUNCH_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_WAVE_LAUNCH_CMD as
 function signature(p RRL_PICK_RESERVATION%rowtype) return varchar2 is j json_object_t:=json_object_t();
 begin
  j.put('id',p.PICK_RESERVATION_ID);j.put('plan',p.PICK_PLAN_ID);j.put('line',p.PICK_PLAN_LINE_ID);j.put('task',p.PICK_TASK_ID);
  j.put('uid',p.PALLET_UID);j.put('cell',p.SOURCE_CELL_CODE);j.put('article',p.ARTICUL);j.put('qty',RRL_STOCK_PLAN_HELPER.decimal_text(p.RESERVED_QTY));
  j.put('status',p.RESERVATION_STATUS);j.put('level',p.RESERVATION_LEVEL);
  j.put('customer',p.CUSTOMER_ID);j.put('order',p.CUSTOMER_ORDER_ID);
  return rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v_wave number;v_ware number;v_id number;v_uom varchar2(20);v_ver number;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;
 begin
  v_wave:=d.get_object('source').get_number('wave_id');select WARE_ID into v_ware from RRL_PICK_WAVE where PICK_WAVE_ID=v_wave;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v_wave));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  for o in(select * from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=v_wave and STATUS='ACTIVE' order by PICK_WAVE_ORDER_ID) loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(o.PICK_WAVE_ORDER_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(o.PICK_PLAN_ID));
   for t in(select PICK_TASK_ID from RRL_PICK_TASK where PICK_PLAN_ID=o.PICK_PLAN_ID order by PICK_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.PICK_TASK_ID));
   end loop;
  end loop;
  for pr in(select pr.* from RRL_PICK_RESERVATION pr join RRL_PICK_WAVE_ORDER wo on wo.PICK_PLAN_ID=pr.PICK_PLAN_ID
   where wo.PICK_WAVE_ID=v_wave and wo.STATUS='ACTIVE' and pr.RESERVATION_STATUS='ACTIVE' and pr.RESERVATION_LEVEL='SOFT' order by pr.PICK_RESERVATION_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'WAVE_LAUNCH_BATCH_BOUND');end if;
   if pr.PALLET_UID is null or pr.SOURCE_CELL_CODE is null or pr.RESERVED_QTY<=0 then raise_application_error(-20884,'WAVE_SOURCE_IDENTITY_REQUIRED');end if;
   select BASE_UOM into v_uom from RRL_REMAINS where UID_POLETA=pr.PALLET_UID and CELL=pr.SOURCE_CELL_CODE;
   select max(POLICY_VERSION) into v_ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=pr.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
   if v_ver is null then raise_application_error(-20868,'WAVE_BASE_POLICY_REQUIRED');end if;
   select RRL_STOCK_RESERVATION_SQ.nextval into v_id from dual;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(pr.PICK_RESERVATION_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,pr.PALLET_UID,pr.ARTICUL,pr.SOURCE_CELL_CODE,null);
   x:=json_object_t();x.put('projection_id',pr.PICK_RESERVATION_ID);x.put('reservation_id',v_id);x.put('signature',signature(pr));
   x.put('uom',v_uom);x.put('version',v_ver);a.append(x);
  end loop;
  if a.get_size=0 then raise_application_error(-20886,'WAVE_NO_SOFT_RESERVATIONS');end if;
  v.put('wave',v_wave);v.put('warehouse',v_ware);v.put('reservations',a);p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();details json_object_t;
  a json_array_t;plan clob;status varchar2(30);cnt number;ware number;ready number;units clob;pr RRL_PICK_RESERVATION%rowtype;
 begin
  if RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')!=1 then raise_application_error(-20882,'WAVE_LAUNCH_FORBIDDEN');end if;
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;
end;v:=json_object_t.parse(plan).get_object('domain');a:=v.get_array('reservations');
  declare
 v_json_sql_2_1 number:=v.get_number('wave');
begin
select STATUS,WARE_ID into status,ware from RRL_PICK_WAVE where PICK_WAVE_ID=v_json_sql_2_1 for update;
end;
  if status not in('DRAFT','PREVIEW') or ware!=v.get_number('warehouse') then raise_application_error(-20886,'WAVE_NOT_LAUNCHABLE');end if;
  declare
 v_json_sql_3_1 number:=v.get_number('wave');
begin
select count(*) into cnt from RRL_PICK_RESERVATION pr join RRL_PICK_WAVE_ORDER wo on wo.PICK_PLAN_ID=pr.PICK_PLAN_ID
   where wo.PICK_WAVE_ID=v_json_sql_3_1 and wo.STATUS='ACTIVE' and pr.RESERVATION_STATUS='ACTIVE' and pr.RESERVATION_LEVEL='SOFT';
end;
  if cnt!=a.get_size then raise_application_error(-20890,'CLOSURE_CHANGED: wave sources');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);declare
 v_json_sql_4_1 number:=x.get_number('projection_id');
begin
select * into pr from RRL_PICK_RESERVATION where PICK_RESERVATION_ID=v_json_sql_4_1 for update;
end;
   if signature(pr)!=x.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: wave reservation');end if;
   RRL_STOCK_LOCATION_CORE.assert_ordinary(pr.SOURCE_CELL_CODE,ware,'SOURCE');
   select nvl(br.IS_SHIPMENT_ALLOWED,1) into ready from RRL_PALLETS pp left join RRL_PROD_BATCH_READY_V br on br.PROD_BATCH_ID=pp.PROD_BATCH_ID where pp.UID_PALLET=pr.PALLET_UID;
   if ready!=1 then raise_application_error(-20886,'WAVE_SOURCE_REGULATORY_NOT_READY');end if;
   units:=RRL_STOCK_UNIT_CORE.automatic_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,pr.RESERVED_QTY);
   details:=json_object_t();details.put('reservation_scope','QTY');details.put('pick_wave_id',v.get_number('wave'));
   details.put('pick_plan_id',pr.PICK_PLAN_ID);details.put('pick_plan_line_id',pr.PICK_PLAN_LINE_ID);
   details.put('customer_order_id',pr.CUSTOMER_ORDER_ID);details.put('customer_id',pr.CUSTOMER_ID);
   RRL_STOCK_RESERVE_CORE.create_hard(x.get_number('reservation_id'),pr.PALLET_UID,pr.SOURCE_CELL_CODE,pr.RESERVED_QTY,x.get_string('uom'),x.get_number('version'),
    'PICK_WAVE',v.get_number('wave'),pr.PICK_TASK_ID,'PICKING',p_actor,details.to_clob);
   RRL_STOCK_UNIT_CORE.reserve_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,x.get_number('reservation_id'),pr.RESERVED_QTY,units);
  end loop;
  RRL_PICK_WAVE_META.launch_wave(v.get_number('wave'),p_actor);
  j.put('operation_id',d.get_string('operation_id'));j.put('wave_id',v.get_number('wave'));j.put('reserved_count',a.get_size);j.put('status','LAUNCHED');p_result:=j.to_clob;
 end;
end;
/
