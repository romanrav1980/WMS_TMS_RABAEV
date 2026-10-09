create or replace package RRL_STOCK_MES_MOVEMENT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE) as
 function signature(p_m RRL_MES_MOVEMENT%rowtype) return varchar2;
 procedure compile_movements(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
end;
/
create or replace package body RRL_STOCK_MES_MOVEMENT_PLAN as
 function signature(p_m RRL_MES_MOVEMENT%rowtype) return varchar2 is v json_object_t:=json_object_t();
 begin
  v.put('id',p_m.MOVEMENT_ID);v.put('type',p_m.MOVEMENT_TYPE);v.put('order',p_m.PRODUCTION_ORDER_ID);
  v.put('uid',p_m.UID_PALLET);v.put('sscc',p_m.SSCC);v.put('batch',p_m.PROD_BATCH_ID);v.put('raw',p_m.RAW_ARTICUL);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_m.QUANTITY));v.put('unit',p_m.UNIT_CODE);
  v.put('from',p_m.SOURCE_LOCATION);v.put('to',p_m.TARGET_LOCATION);
  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_movements(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;ids json_array_t;a json_array_t:=json_array_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v json_object_t:=json_object_t();h json_object_t:=json_object_t();
  m RRL_MES_MOVEMENT%rowtype;o RRL_PRODUCTION_ORDER%rowtype;v_id number;v_article varchar2(160);
  v_p number;v_target varchar2(200);v_reservation number;v_new_reservation number;v_qty number;
  v_num number;v_den number;v_scale number;v_base varchar2(20);v_version number;
  type quantity_map is table of number index by varchar2(2000);v_balances quantity_map;v_target_reservations quantity_map;
  type identity_map is table of varchar2(200) index by varchar2(2000);v_targets identity_map;
  v_source_key varchar2(2000);v_target_key varchar2(2000);v_physical_uid varchar2(200);
  function projected(p_uid varchar2,p_cell varchar2) return number is k varchar2(2000);n number;
  begin
   k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid,p_cell));
   if not v_balances.exists(k) then
    begin select REMAIN into n from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;exception when no_data_found then n:=0;end;
    v_balances(k):=n;
   end if;
   return v_balances(k);
  end;

 begin
  s:=d.get_object('source');ids:=s.get_array('movement_ids');
  if ids is null or ids.get_size<1 or ids.get_size>200 then raise_application_error(-20871,'MES_MOVEMENT_BATCH_SIZE');end if;
  declare
 v_json_sql_1_1 number:=s.get_number('production_order_id');
begin
select * into o from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=v_json_sql_1_1;
end;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRODUCTION_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(o.PRODUCTION_ORDER_ID));
  for i in 0..ids.get_size-1 loop
   v_id:=ids.get_number(i);select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=v_id;
   if m.PRODUCTION_ORDER_ID!=o.PRODUCTION_ORDER_ID or m.UID_PALLET is null
    or m.MOVEMENT_TYPE not in('RAW_ISSUE_TO_PRODUCTION','RAW_CONSUMPTION','FG_PALLET_RELEASE') then
    raise_application_error(-20886,'MES_MOVEMENT_IDENTITY_CONFLICT');end if;
   v_physical_uid:=m.UID_PALLET;
   v_source_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',m.UID_PALLET,m.SOURCE_LOCATION));
   if m.MOVEMENT_TYPE='RAW_CONSUMPTION' and v_targets.exists(v_source_key) then v_physical_uid:=v_targets(v_source_key);end if;
   if m.MOVEMENT_TYPE='FG_PALLET_RELEASE' then v_article:=o.TARGET_ARTICUL;
   else select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=m.UID_PALLET;end if;
   select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=m.UNIT_CODE;
   select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
    from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=m.UNIT_CODE and POLICY_VERSION=v_version;
   v_qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(m.QUANTITY),v_num,v_den,v_scale);
   select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_base and BASE_UOM=v_base and NUMERATOR=1 and DENOMINATOR=1;
   if v_version is null then raise_application_error(-20868,'MES_BASE_POLICY_REQUIRED');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_MES_MOVEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_physical_uid,v_article,
    case when m.MOVEMENT_TYPE!='FG_PALLET_RELEASE' then m.SOURCE_LOCATION end,
    case when m.MOVEMENT_TYPE!='RAW_CONSUMPTION' then m.TARGET_LOCATION end);
   v_target:=v_physical_uid;v_reservation:=null;v_new_reservation:=null;v_p:=null;
   if m.MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION' then
    v_p:=projected(v_physical_uid,m.SOURCE_LOCATION);
    if v_qty<v_p then
     v_target:='PART:'||substr(rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v_id),'AL32UTF8'),sys.dbms_crypto.hash_sh256)),1,64);
     select RRL_STOCK_RESERVATION_SQ.nextval into v_new_reservation from dual;
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_new_reservation));
     RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v_target);RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',v_target);
     RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||v_target);
    end if;
   end if;
   if m.MOVEMENT_TYPE!='FG_PALLET_RELEASE' then
    begin select RESERVATION_ID into v_reservation from RRL_STOCK_RESERVATION where UID_PALLET=m.UID_PALLET and CELL=m.SOURCE_LOCATION
     and SOURCE_DOC_TYPE='PRODUCTION_ORDER' and SOURCE_DOC_ID=o.PRODUCTION_ORDER_ID and RESERVATION_KIND='HARD'
     and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>=v_qty;
    exception when no_data_found then null;when too_many_rows then raise_application_error(-20869,'MES_RESERVATION_AMBIGUOUS');end;
   else RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||m.UID_PALLET);end if;
   if m.MOVEMENT_TYPE='RAW_CONSUMPTION' and v_target_reservations.exists(v_source_key) then v_reservation:=v_target_reservations(v_source_key);end if;
   if m.MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION' then
    v_source_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_physical_uid,m.SOURCE_LOCATION));
    v_balances(v_source_key):=projected(v_physical_uid,m.SOURCE_LOCATION)-v_qty;
    v_target_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_target,m.TARGET_LOCATION));
    v_balances(v_target_key):=projected(v_target,m.TARGET_LOCATION)+v_qty;
    v_target_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',m.UID_PALLET,m.TARGET_LOCATION));
    if v_targets.exists(v_target_key) and v_targets(v_target_key)!=v_target then
     raise_application_error(-20886,'MES_CONSUMPTION_REQUIRES_PHYSICAL_PALLET_ALLOCATION');end if;
    v_targets(v_target_key):=v_target;
    if v_reservation is not null then v_target_reservations(v_target_key):=case when v_target=m.UID_PALLET then v_reservation else v_new_reservation end;end if;
   elsif m.MOVEMENT_TYPE='RAW_CONSUMPTION' then
    v_source_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_physical_uid,m.SOURCE_LOCATION));
    if projected(v_physical_uid,m.SOURCE_LOCATION)<v_qty then raise_application_error(-20868,'MES_CONSUMPTION_STOCK_INSUFFICIENT');end if;
    v_balances(v_source_key):=v_balances(v_source_key)-v_qty;
   end if;
   v:=json_object_t();v.put('physical_uid',v_physical_uid);v.put('movement_id',v_id);v.put('signature',signature(m));v.put('article',v_article);
   v.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));v.put('base_uom',v_base);v.put('uom_version',v_version);
   v.put('source_p',case when v_p is not null then RRL_STOCK_PLAN_HELPER.decimal_text(v_p) end);
   v.put('target_uid',v_target);v.put('reservation_id',v_reservation);v.put('new_reservation_id',v_new_reservation);a.append(v);
  end loop;
  h.put('production_order_id',o.PRODUCTION_ORDER_ID);h.put('movements',a);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=h.to_clob;
 end;
end;
/
