declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_RESERVATION_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_RESERVATION_CMD as
 procedure source_anchor(p_r in out nocopy json_array_t,p_type varchar2,p_id number) is v_table varchar2(40);
 begin
  if p_id is null or p_id<1 or p_id!=trunc(p_id) then raise_application_error(-20869,'RESERVATION_DOCUMENT_REQUIRED');end if;
  case p_type when 'PRODUCTION_ORDER' then v_table:='RRL_PRODUCTION_ORDER';
   when 'PICK_WAVE' then v_table:='RRL_PICK_WAVE';when 'PICK_PLAN' then v_table:='RRL_PICK_PLAN';
   else raise_application_error(-20869,'RESERVATION_DOCUMENT_TYPE_UNSUPPORTED');end case;
  RRL_STOCK_PLAN_HELPER.row_key(p_r,v_table,RRL_STOCK_PLAN_HELPER.decimal_text(p_id));
 end;
 procedure validate_source(p_type varchar2,p_id number,p_allow_closed number default 0) is v_status varchar2(40);
 begin
  case p_type when 'PRODUCTION_ORDER' then
    select STATUS into v_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=p_id for update;
   when 'PICK_WAVE' then select STATUS into v_status from RRL_PICK_WAVE where PICK_WAVE_ID=p_id for update;
   when 'PICK_PLAN' then select STATUS into v_status from RRL_PICK_PLAN where PICK_PLAN_ID=p_id for update;
   else raise_application_error(-20869,'RESERVATION_DOCUMENT_TYPE_UNSUPPORTED');end case;
  if p_allow_closed=0 and (v_status is null or v_status in('CANCELLED','CLOSED','COMPLETED','SHIPPED')) then
   raise_application_error(-20869,'RESERVATION_DOCUMENT_NOT_OPEN');end if;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;s json_object_t;
  r json_array_t:=json_array_t();f json_array_t:=json_array_t();v json_object_t:=json_object_t();
  old RRL_STOCK_RESERVATION%rowtype;v_id number;v_uid varchar2(200);v_cell varchar2(60);v_article varchar2(160);
  v_type varchar2(50);v_doc number;v_version number;
 begin
  m:=d.get_object('metadata');s:=d.get_object('source');
  if d.get_string('command_type')='RESERVATION_CREATE' then
   select RRL_STOCK_RESERVATION_SQ.nextval into v_id from dual;
   v_uid:=m.get_string('uid_pallet');v_cell:=m.get_string('cell');v_article:=m.get_string('articul');
   v_type:=m.get_string('source_doc_type');v_doc:=m.get_number('source_doc_id');
  else
   v_id:=s.get_number('reservation_id');
   select * into old from RRL_STOCK_RESERVATION where RESERVATION_ID=v_id;
   v_uid:=old.UID_PALLET;v_cell:=old.CELL;v_article:=old.ARTICUL;v_type:=old.SOURCE_DOC_TYPE;v_doc:=old.SOURCE_DOC_ID;
   v_version:=old.RESERVATION_VERSION;
   if d.get_string('command_type')='RESERVATION_PROMOTE' then
    v_uid:=m.get_string('uid_pallet');v_cell:=m.get_string('cell');
   end if;
  end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
  source_anchor(r,v_type,v_doc);
  if v_uid is not null and v_cell is not null then RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_uid,v_article,v_cell,null);
  else RRL_STOCK_PLAN_HELPER.fence(f,'SKU',v_article);end if;
  v.put('reservation_id',v_id);v.put('uid',v_uid);v.put('cell',v_cell);v.put('article',v_article);
  v.put('doc_type',v_type);v.put('doc_id',v_doc);v.put('version',v_version);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;v json_object_t;j json_object_t:=json_object_t();
  old RRL_STOCK_RESERVATION%rowtype;v_plan clob;v_id number;v_kind varchar2(80);v_qty number;v_input varchar2(20);
  v_base varchar2(20);v_num number;v_den number;v_scale number;v_version number;v_ware number;v_article varchar2(160);
  v_uid varchar2(200);v_cell varchar2(60);v_type varchar2(50);v_doc number;v_units clob;v_event number;v_n number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_reservation_edit')!=1 then raise_application_error(-20882,'RESERVATION_FORBIDDEN');end if;
  m:=d.get_object('metadata');v_kind:=d.get_string('command_type');
  if v_kind='RESERVATION_CREATE' and (m.get_string('reservation_kind') is null or m.get_string('reservation_kind') not in('SOFT','HARD')) then raise_application_error(-20869,'RESERVATION_KIND_INVALID');end if;
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;
end;
  v:=json_object_t.parse(v_plan).get_object('domain');
  v_id:=v.get_number('reservation_id');v_uid:=v.get_string('uid');v_cell:=v.get_string('cell');
  v_article:=v.get_string('article');v_type:=v.get_string('doc_type');v_doc:=v.get_number('doc_id');
  validate_source(v_type,v_doc,case when v_kind in('RESERVATION_RELEASE','RESERVATION_CANCEL') then 1 else 0 end);
  if v_kind!='RESERVATION_CREATE' then
   select * into old from RRL_STOCK_RESERVATION where RESERVATION_ID=v_id for update;
   if old.RESERVATION_VERSION!=v.get_number('version') or old.SOURCE_DOC_TYPE!=v_type or old.SOURCE_DOC_ID!=v_doc
    or (v_kind!='RESERVATION_PROMOTE' and (old.UID_PALLET!=v_uid or old.CELL!=v_cell)) then
    raise_application_error(-20890,'CLOSURE_CHANGED: reservation');end if;
  end if;
  -- Release/cancellation remains legal after its source document is closed.

  if d.get_array('units').get_size>0 then v_units:=d.get_array('units').to_clob;end if;
  if v_kind='RESERVATION_CREATE' and (m.get_string('reservation_scope') is null or m.get_string('reservation_scope') not in('PALLET','QTY')) then raise_application_error(-20869,'RESERVATION_SCOPE_INVALID');end if;
  if v_kind='RESERVATION_CREATE' and m.get_string('reservation_kind')='SOFT' then
   if m.get_string('uid_pallet') is not null or m.get_string('cell') is not null or m.get_number('ware_id') is not null or m.get_string('batch_id') is not null or m.get_number('prod_batch_id') is not null or m.get_string('sscc') is not null then raise_application_error(-20869,'SOFT_HAS_PHYSICAL_BINDING');end if;
   v_qty:=RRL_STOCK_MATH.quantity(m.get_string('qty'));
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,v_id);
   declare
 v_json_sql_2_1 varchar2(32767):=m.get_string('reservation_scope');
 v_json_sql_2_2 varchar2(32767):=m.get_string('reservation_domain');
 v_json_sql_2_3 number:=m.get_number('source_line_id');
 v_json_sql_2_4 number:=m.get_number('task_id');
 v_json_sql_2_5 number:=m.get_number('customer_id');
 v_json_sql_2_6 number:=m.get_number('customer_order_id');
 v_json_sql_2_7 number:=m.get_number('pick_plan_line_id');
 v_json_sql_2_8 number:=m.get_number('pick_wave_line_id');
 v_json_sql_2_9 varchar2(32767):=m.get_string('unit_code');
 v_json_sql_2_10 number:=m.get_number('priority');
begin
insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,
    SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,TASK_ID,CUSTOMER_ID,CUSTOMER_ORDER_ID,PRODUCTION_ORDER_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,PICK_WAVE_ID,PICK_WAVE_LINE_ID,ARTICUL,QTY,UNIT_CODE,STATUS,PRIORITY,CREATED_BY,RESERVATION_VERSION)
    values(v_id,'SOFT',v_json_sql_2_1,v_json_sql_2_2,v_type,v_doc,
     v_json_sql_2_3,v_json_sql_2_4,v_json_sql_2_5,v_json_sql_2_6,
     case when v_type='PRODUCTION_ORDER' then v_doc else null end,case when v_type='PICK_PLAN' then v_doc else null end,v_json_sql_2_7,case when v_type='PICK_WAVE' then v_doc else null end,v_json_sql_2_8,v_article,v_qty,v_json_sql_2_9,'ACTIVE',nvl(v_json_sql_2_10,100),p_actor,0);
end;
   RRL_STOCK_CTX_API.end_effect;
  elsif old.RESERVATION_KIND='SOFT' and v_kind in('RESERVATION_RELEASE','RESERVATION_CANCEL') then
   if old.STATUS not in('ACTIVE','ALLOCATED') then raise_application_error(-20869,'SOFT_RELEASE_STATE_CONFLICT');end if;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,v_id);
   update RRL_STOCK_RESERVATION set STATUS=case when v_kind='RESERVATION_CANCEL' then 'CANCELLED' else 'RELEASED' end,
    RELEASED_AT=systimestamp,RELEASED_BY=p_actor,RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=v_id;
   RRL_STOCK_CTX_API.end_effect;
  else
   if v_uid is null or v_cell is null then raise_application_error(-20869,'HARD_STOCK_REQUIRED');end if;
   select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=v_uid;
   if v_article!=v.get_string('article') then raise_application_error(-20869,'RESERVATION_ARTICLE_CONFLICT');end if;
   select WARE_ID into v_ware from RRL_CELLS where CELL=v_cell;
   if v_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE') then
    RRL_STOCK_LOCATION_CORE.assert_ordinary(v_cell,v_ware,'SOURCE');
    if m.get_number('ware_id') is null or m.get_number('ware_id')!=v_ware then raise_application_error(-20869,'RESERVATION_WAREHOUSE_CONFLICT');end if;
    v_input:=nvl(m.get_string('unit_code'),old.UNIT_CODE);
    v_qty:=case when m.has('qty') and not m.get('qty').is_null then RRL_STOCK_MATH.quantity(m.get_string('qty')) else old.QTY end;
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input;
    select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
     from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input and POLICY_VERSION=v_version;
    v_qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(v_qty),v_num,v_den,v_scale);
    if v_kind='RESERVATION_PROMOTE' then
     if old.RESERVATION_KIND!='SOFT' or old.STATUS not in('ACTIVE','ALLOCATED') then raise_application_error(-20869,'SOFT_PROMOTION_CONFLICT');end if;
     RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,0,v_qty,v_base,v_version);
     RRL_STOCK_CTX_API.begin_effect('RESERVATION',v_uid,v_cell,v_id);
     declare
 v_json_sql_3_1 varchar2(32767):=m.get_string('reservation_scope');
begin
update RRL_STOCK_RESERVATION set RESERVATION_KIND='HARD',RESERVATION_SCOPE=v_json_sql_3_1,
      UID_PALLET=v_uid,CELL=v_cell,WARE_ID=v_ware,QTY=v_qty,UNIT_CODE=v_base,BASE_QTY=v_qty,BASE_UOM=v_base,
      STATUS='ACTIVE',RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=v_id;
end;
     RRL_STOCK_CTX_API.end_effect;
    else RRL_STOCK_RESERVE_CORE.create_hard(v_id,v_uid,v_cell,v_qty,v_base,v_version,v_type,v_doc,
      m.get_number('source_line_id'),m.get_string('reservation_domain'),p_actor,m.to_clob);end if;
    select nvl(max(MARKING_REQUIRED),0) into v_n from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
    if v_n=1 then
     select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
     if v_n=0 then raise_application_error(-20884,'MARKED_BINDING_REQUIRED');end if;
    end if;
    RRL_STOCK_UNIT_CORE.reserve_units(v_uid,v_cell,v_id,v_qty,v_units);
   else
    v_qty:=old.BASE_QTY;v_base:=old.BASE_UOM;
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_base and BASE_UOM=v_base and NUMERATOR=DENOMINATOR;
    if v_kind='RESERVATION_CONSUME' then
     RRL_STOCK_LOCATION_CORE.assert_ordinary(v_cell,v_ware,'SOURCE');
     RRL_STOCK_UNIT_CORE.release_units(v_id,v_qty,v_units,1);
     RRL_STOCK_RESERVE_CORE.consume_hard(v_id,v_qty,v_version,v_type,v_doc,p_actor);
     RRL_STOCK_BALANCE_CORE.write_leg(v_uid,v_cell,null,-v_qty,v_base,v_version,1,1,3,p_actor,v_event);
    else
     RRL_STOCK_UNIT_CORE.release_units(v_id,v_qty,v_units,0);
     RRL_STOCK_RESERVE_CORE.release_hard(v_id,v_qty,v_version,v_type,v_doc,p_actor);
     if v_kind='RESERVATION_CANCEL' then RRL_STOCK_CTX_API.begin_effect('RESERVATION',v_uid,v_cell,v_id);update RRL_STOCK_RESERVATION set STATUS='CANCELLED',RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=v_id;RRL_STOCK_CTX_API.end_effect;end if;
    end if;
   end if;
  end if;
  j.put('operation_id',d.get_string('operation_id'));j.put('reservation_id',v_id);j.put('action',v_kind);p_result:=j.to_clob;
 end;
end;
/
