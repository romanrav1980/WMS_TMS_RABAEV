create or replace package RRL_STOCK_INTERNAL_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_move(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_INTERNAL_CMD as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();p RRL_PALLETS%rowtype;
  v_from varchar2(60);v_to varchar2(60);v_p number;v_qty number;v_base varchar2(20);v_ver number;
  v_ware number;v_source_ware number;v_target varchar2(200);v_uom_version number;v_sig varchar2(64);v_input varchar2(20);
 begin
  m:=d.get_object('metadata');m.on_error(1);
  declare
 v_json_sql_1_1 varchar2(32767):=m.get_string('uid');
begin
select * into p from RRL_PALLETS where UID_PALLET=v_json_sql_1_1;
end;
  v_to:=m.get_string('target_cell');
  if m.has('source_cell') and not m.get('source_cell').is_null then v_from:=m.get_string('source_cell');
  else select CELL into v_from from RRL_REMAINS where UID_POLETA=p.UID_PALLET and REMAIN>0;end if;
  select REMAIN,BASE_UOM,STOCK_VERSION into v_p,v_base,v_ver from RRL_REMAINS where UID_POLETA=p.UID_PALLET and CELL=v_from;
  select WARE_ID into v_ware from RRL_CELLS where CELL=v_to;
  select WARE_ID into v_source_ware from RRL_CELLS where CELL=v_from;
  if v_source_ware!=v_ware or v_ware is null then raise_application_error(-20886,'INTERNAL_WAREHOUSE_CONFLICT');end if;
  v_input:=nvl(m.get_string('unit'),v_base);
  if m.get_string('quantity')='0' then
   RRL_STOCK_PALLET_UOM.resolve_quantity(p.UID_PALLET,v_base,RRL_STOCK_PLAN_HELPER.decimal_text(v_p),v_base,v_qty,v_uom_version,v_sig);
  else RRL_STOCK_PALLET_UOM.resolve_quantity(p.UID_PALLET,v_input,m.get_string('quantity'),v_base,v_qty,v_uom_version,v_sig);end if;
  v_target:=p.UID_PALLET;
  if v_qty<v_p then v_target:='PART:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256));end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,p.UID_PALLET,p.ARTICUL,v_from,v_to);
  if p.PRIHOD_NAKLAD_ID is not null and p.PRIHOD_NAKLAD_ID>0 then
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(p.PRIHOD_NAKLAD_ID));
  end if;
  if v_target!=p.UID_PALLET then
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v_target);RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',v_target);
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||v_target);
  end if;
  v.put('uid',p.UID_PALLET);v.put('target_uid',v_target);v.put('article',p.ARTICUL);v.put('from',v_from);v.put('to',v_to);
  v.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(v_p));v.put('stock_version',v_ver);v.put('base_uom',v_base);
  v.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));v.put('uom_version',v_uom_version);v.put('uom_signature',v_sig);v.put('warehouse',v_ware);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_move(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;v json_object_t;j json_object_t:=json_object_t();
  p RRL_PALLETS%rowtype;c RRL_CELLS%rowtype;v_plan clob;v_uid varchar2(200);v_target varchar2(200);
  v_p number;v_ver number;v_qty number;v_base varchar2(20);v_uom_version number;v_sig varchar2(64);
  v_n number;v_input varchar2(20);v_condition number;v_pick_cell varchar2(60);v_stop number;v_weight number;v_units clob;
 begin
  if d.get_string('command_type')='MOVE_QUARANTINE' and RRL_HAS_WRIGHT(p_actor,'QUARANTINE_MOVE')!=1 then raise_application_error(-20882,'QUARANTINE_MOVE_FORBIDDEN');end if;
  if RRL_HAS_WRIGHT(p_actor,'INTERNAL_MOVE')!=1 and RRL_HAS_WRIGHT(p_actor,'stock_posting_manual_move')!=1 then raise_application_error(-20882,'INTERNAL_MOVE_FORBIDDEN');end if;
  declare
 v_json_sql_2_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_2_1;
end;
  v:=json_object_t.parse(v_plan).get_object('domain');m:=d.get_object('metadata');
  v_uid:=v.get_string('uid');v_target:=v.get_string('target_uid');
  select * into p from RRL_PALLETS where UID_PALLET=v_uid;
  if p.ARTICUL!=v.get_string('article') then raise_application_error(-20890,'CLOSURE_CHANGED: pallet article');end if;
  declare
 v_json_sql_3_1 varchar2(32767):=v.get_string('from');
begin
select REMAIN,BASE_UOM,STOCK_VERSION into v_p,v_base,v_ver from RRL_REMAINS where UID_POLETA=v_uid and CELL=v_json_sql_3_1;
end;
  if v_ver!=v.get_number('stock_version') or RRL_STOCK_PLAN_HELPER.decimal_text(v_p)!=v.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: internal stock');end if;
  v_input:=nvl(m.get_string('unit'),v_base);
  if m.get_string('quantity')='0' then
   RRL_STOCK_PALLET_UOM.resolve_quantity(v_uid,v_base,RRL_STOCK_PLAN_HELPER.decimal_text(v_p),v_base,v_qty,v_uom_version,v_sig);
  else RRL_STOCK_PALLET_UOM.resolve_quantity(v_uid,v_input,m.get_string('quantity'),v_base,v_qty,v_uom_version,v_sig);end if;
  if v_sig!=v.get_string('uom_signature') or RRL_STOCK_PLAN_HELPER.decimal_text(v_qty)!=v.get_string('base_quantity') then raise_application_error(-20890,'CLOSURE_CHANGED: internal UOM');end if;
  if p.PRIHOD_NAKLAD_ID>0 then
   select CONDITION into v_condition from RRL_PRIHOD_NAKLAD where ID=p.PRIHOD_NAKLAD_ID for update;
   if v_condition in(0,1) then raise_application_error(-20886,'NAKLAD_NE_ZAKRYTA');end if;
  end if;
  declare
 v_json_sql_4_1 varchar2(32767):=v.get_string('to');
begin
select * into c from RRL_CELLS where CELL=v_json_sql_4_1;
end;
  if d.get_string('command_type')='MOVE_QUARANTINE' then
   if v_qty!=v_p then raise_application_error(-20886,'QUARANTINE_MOVE_REQUIRES_WHOLE_PALLET');end if;
   declare
 v_json_sql_5_1 varchar2(32767):=v.get_string('from');
begin
select count(*) into v_n from RRL_CELLS where CELL in(v_json_sql_5_1,c.CELL) and nvl(BLOCKED_FOR_REMAINS,0)=1;
end;
   if v_n=0 then raise_application_error(-20879,'QUARANTINE_CELL_REQUIRED');end if;
  end if;
  if nvl(c.OTBOR,0)=0 and nvl(c.IS_SYSTEM,0)=0 then
   select count(*) into v_n from RRL_REMAINS where CELL=c.CELL and REMAIN>0 and UID_POLETA!=v_uid;
   if v_n>0 then raise_application_error(-20886,'CELL_NOT_EMPTY');end if;
  elsif nvl(c.OTBOR,0)=1 then
   select CELL into v_pick_cell from RRL_ARTICULS where ACTICUL=p.ARTICUL;
   if v_pick_cell is null or v_pick_cell!=c.CELL then raise_application_error(-20886,'OTBOR_DRUGOGO_ARTICULA');end if;
  end if;
  select nvl(WEIGHT_LIMIT_STOP,0) into v_stop from RRL_WARES where ID=c.WARE_ID;
  if v_stop=1 and c.LIMIT_WEIGHT is not null then
   if p.WEIGHT_BRUTTO is null or p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20886,'PALLET_WEIGHT_REQUIRED');end if;
   select nvl(sum(pp.WEIGHT_BRUTTO*rr.REMAIN/nullif(pp.UNIT_COUNT,0)),0) into v_weight
    from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA where rr.CELL=c.CELL and rr.REMAIN>0;
   if v_weight+p.WEIGHT_BRUTTO*v_qty/p.UNIT_COUNT>c.LIMIT_WEIGHT then raise_application_error(-20886,'CELL_WEIGHT_LIMIT');end if;
  end if;
  if v_target!=v_uid then
   select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and STOCK_STATUS!='ISSUED';
   if v_n>0 then raise_application_error(-20884,'PARTIAL_MARKED_MOVE_REQUIRES_PHYSICAL_HU_SPLIT');end if;
   p.STOCK_ORIGIN_UID:=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET);p.CREATED_BY_STOCK_OP:=d.get_string('operation_id');
   if p.WEIGHT_BRUTTO is not null then
    if p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20887,'PALLET_BIRTH_QUANTITY_REQUIRED');end if;
    p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*v_qty/p.UNIT_COUNT;
   end if;
   p.UID_PALLET:=v_target;p.SSCC:=null;p.UNIT_COUNT:=v_qty;p.PRINTED:=0;
   insert into RRL_PALLETS values p;
  end if;
  if d.get_array('units').get_size>0 then v_units:=d.get_array('units').to_clob;end if;
  RRL_STOCK_TRANSFER_CORE.move(v_uid,v_target,v.get_string('from'),c.CELL,v_qty,v_base,v_uom_version,c.WARE_ID,p_actor,1,null,v_units,null,null,null,case when d.get_string('command_type')='MOVE_QUARANTINE' then 'QUARANTINE' else 'ORDINARY' end);
  j.put('operation_id',d.get_string('operation_id'));j.put('status','APPLIED');j.put('source_uid',v_uid);j.put('uid',v_target);
  j.put('from_cell',v.get_string('from'));j.put('cell',c.CELL);j.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));j.put('base_uom',v_base);
  p_result:=j.to_clob;
 end;
end;
/
