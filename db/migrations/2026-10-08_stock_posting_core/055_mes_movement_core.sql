create or replace package RRL_STOCK_MES_MOVEMENT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_movements(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_MES_MOVEMENT_CORE as
 procedure execute_movements(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);h json_object_t;v json_object_t;items json_array_t;m RRL_MES_MOVEMENT%rowtype;
  o RRL_PRODUCTION_ORDER%rowtype;p RRL_PALLETS%rowtype;v_plan clob;v_uid varchar2(200);v_target varchar2(200);
  v_qty number;v_base varchar2(20);v_version number;v_source_ware number;v_target_ware number;v_event number;
  v_reservation number;v_new_reservation number;v_p number;v_article varchar2(160);v_units clob;
  result json_object_t:=json_object_t();facts json_array_t:=json_array_t();fact json_object_t;v_n number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'mes_wms_bridge_apply')!=1 then raise_application_error(-20882,'MES_WMS_APPLY_FORBIDDEN');end if;
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;
end;
  h:=json_object_t.parse(v_plan).get_object('domain');items:=h.get_array('movements');
  declare
 v_json_sql_2_1 number:=h.get_number('production_order_id');
begin
select * into o from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=v_json_sql_2_1 for update;
end;
  if o.STATUS='CANCELLED' then raise_application_error(-20886,'MES_ORDER_CANCELLED');end if;
  for i in 0..items.get_size-1 loop
   v:=treat(items.get(i) as json_object_t);
   declare
 v_json_sql_3_1 number:=v.get_number('movement_id');
begin
select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=v_json_sql_3_1 for update;
end;
   if RRL_STOCK_MES_MOVEMENT_PLAN.signature(m)!=v.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: MES movement');end if;
   if m.STATUS not in('MES_POSTED','ERROR') or m.STATUS is null then raise_application_error(-20886,'MES_MOVEMENT_STATE_CONFLICT');end if;
   v_uid:=v.get_string('physical_uid');v_target:=v.get_string('target_uid');v_article:=v.get_string('article');
   v_qty:=RRL_STOCK_MATH.quantity(v.get_string('base_quantity'));v_base:=v.get_string('base_uom');v_version:=v.get_number('uom_version');
   v_reservation:=v.get_number('reservation_id');v_new_reservation:=v.get_number('new_reservation_id');v_units:=null;
   if d.get_object('metadata').has('units_by_movement') then
    if d.get_object('metadata').get_object('units_by_movement').has(RRL_STOCK_PLAN_HELPER.decimal_text(m.MOVEMENT_ID)) then
     v_units:=d.get_object('metadata').get_object('units_by_movement').get_array(RRL_STOCK_PLAN_HELPER.decimal_text(m.MOVEMENT_ID)).to_clob;
    end if;
   end if;
   if m.MOVEMENT_TYPE='FG_PALLET_RELEASE' then
    select WARE_ID into v_target_ware from RRL_CELLS where CELL=m.TARGET_LOCATION;
    if v_target_ware!=o.WARE_ID then raise_application_error(-20886,'MES_FINISHED_WAREHOUSE_CONFLICT');end if;
    RRL_STOCK_LOCATION_CORE.assert_ordinary(m.TARGET_LOCATION,v_target_ware,'TARGET');
    select count(*) into v_n from RRL_REMAINS where UID_POLETA=v_uid;
    if v_n>0 then raise_application_error(-20886,'MES_FINISHED_STOCK_ALREADY_EXISTS');end if;
    select count(*) into v_n from RRL_PALLETS where UID_PALLET=v_uid;
    if v_n=0 then
     insert into RRL_PALLETS(UID_PALLET,ARTICUL,UNIT_COUNT,PRIHOD_NAKLAD_ID,PROD_BATCH_ID,SSCC,QUALITY_STATUS)
      values(v_uid,v_article,v_qty,0,m.PROD_BATCH_ID,m.SSCC,'RELEASED');
    else
     select * into p from RRL_PALLETS where UID_PALLET=v_uid;
     if p.ARTICUL!=v_article or p.PROD_BATCH_ID!=m.PROD_BATCH_ID or p.UNIT_COUNT!=v_qty then raise_application_error(-20887,'MES_FINISHED_LOT_CONFLICT');end if;
    end if;
    RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,m.TARGET_LOCATION,v_qty,0,v_base,v_version);
    RRL_STOCK_UNIT_CORE.admit_captured(v_uid,m.TARGET_LOCATION);
    RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,m.TARGET_LOCATION,v_qty,v_base,v_version,i+1,1,1,p_actor,v_event);
   else
    select * into p from RRL_PALLETS where UID_PALLET=v_uid;
    if p.ARTICUL!=v_article or (m.RAW_ARTICUL is not null and m.RAW_ARTICUL!=v_article) then raise_application_error(-20887,'MES_RAW_ARTICLE_CONFLICT');end if;
    select WARE_ID into v_source_ware from RRL_CELLS where CELL=m.SOURCE_LOCATION;
    if v_reservation is not null then
     select count(*) into v_n from RRL_STOCK_RESERVATION where RESERVATION_ID=v_reservation and
      SOURCE_DOC_TYPE='PRODUCTION_ORDER' and SOURCE_DOC_ID=o.PRODUCTION_ORDER_ID and UID_PALLET=v_uid and CELL=m.SOURCE_LOCATION;
     if v_n!=1 then raise_application_error(-20869,'MES_RESERVATION_OWNER_CONFLICT');end if;
    end if;
    if m.MOVEMENT_TYPE='RAW_CONSUMPTION' then
     RRL_STOCK_EFFECT_CORE.consume(v_uid,m.SOURCE_LOCATION,v_qty,v_base,v_version,v_source_ware,p_actor,i+1,
      v_reservation,'PRODUCTION_ORDER',o.PRODUCTION_ORDER_ID,v_units);
    else
     select WARE_ID into v_target_ware from RRL_CELLS where CELL=m.TARGET_LOCATION;
     if v_target_ware!=o.WARE_ID then raise_application_error(-20886,'MES_PRODUCTION_WAREHOUSE_CONFLICT');end if;
     select REMAIN into v_p from RRL_REMAINS where UID_POLETA=v_uid and CELL=m.SOURCE_LOCATION;
     if RRL_STOCK_PLAN_HELPER.decimal_text(v_p)!=v.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: MES source quantity');end if;
     if v_target!=v_uid then
      p.STOCK_ORIGIN_UID:=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET);p.CREATED_BY_STOCK_OP:=d.get_string('operation_id');
      if p.WEIGHT_BRUTTO is not null then
       if p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20887,'PALLET_BIRTH_QUANTITY_REQUIRED');end if;
       p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*v_qty/p.UNIT_COUNT;
      end if;
      p.UID_PALLET:=v_target;p.SSCC:=null;p.UNIT_COUNT:=v_qty;p.PRINTED:=0;
      insert into RRL_PALLETS values p;
     end if;
     RRL_STOCK_TRANSFER_CORE.move(v_uid,v_target,m.SOURCE_LOCATION,m.TARGET_LOCATION,v_qty,v_base,v_version,v_target_ware,
      p_actor,i+1,v_reservation,v_units,v_new_reservation,null,v_source_ware);
    end if;
   end if;
   declare
 v_json_sql_4_1 varchar2(32767):=d.get_string('operation_id');
begin
update RRL_MES_MOVEMENT set STATUS='APPLIED_TO_WMS',SOURCE_UID_PALLET=v_uid,TARGET_UID_PALLET=v_target,
    UID_PALLET=case when MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION' then v_target else UID_PALLET end,
    STOCK_OPERATION_ID=v_json_sql_4_1,POSTED_BASE_QTY=v_qty,STOCK_BASE_UOM=v_base,
    WMS_APPLIED_AT=sysdate,WMS_APPLIED_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor,LAST_ERROR=null where MOVEMENT_ID=m.MOVEMENT_ID;
end;
   fact:=json_object_t();fact.put('movement_id',m.MOVEMENT_ID);fact.put('uid',v_target);fact.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
   fact.put('base_uom',v_base);facts.append(fact);
  end loop;
  result.put('operation_id',d.get_string('operation_id'));result.put('production_order_id',o.PRODUCTION_ORDER_ID);result.put('movements',facts);p_result:=result.to_clob;
 end;
end;
/
