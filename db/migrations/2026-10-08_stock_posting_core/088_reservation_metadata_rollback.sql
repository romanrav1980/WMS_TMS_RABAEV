declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_RESERVE_CORE authid definer
 accessible by(package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_TRANSFER_CORE) as
 procedure create_hard(p_id number,p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2,p_details clob default null);
 procedure release_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure consume_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure relocate_hard(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
   p_qty number,p_uom_version number,p_actor varchar2);
 procedure move_coverage(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
  p_target_ware number,p_qty number,p_target_slot number,p_actor varchar2,p_result_id out number);
end;
/

create or replace package RRL_STOCK_RESERVATION_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_RESERVE_CORE as
 procedure lock_identity(p_id number) is
 begin
  if p_id is null or p_id<1 or p_id!=trunc(p_id) then raise_application_error(-20876,'RESERVATION_ID_INVALID'); end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',to_char(p_id,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')));
 end;
 procedure check_owner(p_id number,p_qty number,p_doc_type varchar2,p_doc_id number,p_r out RRL_STOCK_RESERVATION%rowtype) is
 begin
  lock_identity(p_id);
  select * into p_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if p_r.RESERVATION_KIND is null or p_r.RESERVATION_KIND!='HARD' or p_r.STATUS is null or p_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
   or p_r.BASE_QTY is null or p_r.BASE_UOM is null or p_qty is null or p_qty<=0 or p_qty>p_r.BASE_QTY
   or p_doc_type is null or p_doc_id is null or p_r.SOURCE_DOC_TYPE is null or p_r.SOURCE_DOC_ID is null or p_r.SOURCE_DOC_TYPE!=p_doc_type or p_r.SOURCE_DOC_ID!=p_doc_id then
   raise_application_error(-20869,'RESERVATION_CONFLICT');
  end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_r.UID_PALLET));
 end;
 procedure decrease(p_r RRL_STOCK_RESERVATION%rowtype,p_qty number,p_status varchar2,p_actor varchar2) is
 begin
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_r.UID_PALLET,p_r.CELL,p_r.RESERVATION_ID);
  update RRL_STOCK_RESERVATION set BASE_QTY=BASE_QTY-p_qty,QTY=BASE_QTY-p_qty,UNIT_CODE=BASE_UOM,
   STATUS=case when BASE_QTY=p_qty then p_status else STATUS end,
   CONSUMED_AT=case when BASE_QTY=p_qty and p_status='CONSUMED' then systimestamp else CONSUMED_AT end,
   CONSUMED_BY=case when BASE_QTY=p_qty and p_status='CONSUMED' then p_actor else CONSUMED_BY end,
   RELEASED_AT=case when BASE_QTY=p_qty and p_status='RELEASED' then systimestamp else RELEASED_AT end,
   RELEASED_BY=case when BASE_QTY=p_qty and p_status='RELEASED' then p_actor else RELEASED_BY end,
   RESERVATION_VERSION=RESERVATION_VERSION+1
   where RESERVATION_ID=p_r.RESERVATION_ID and RESERVATION_VERSION=p_r.RESERVATION_VERSION;
  if sql%rowcount!=1 then raise_application_error(-20867,'VERSION_CONFLICT'); end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure create_hard(p_id number,p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2,p_details clob default null) is v_article varchar2(160);v_ware number;v_details json_object_t;
 begin
  lock_identity(p_id);
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_cell;
  if p_qty is null or p_qty<=0 or p_doc_id is null or p_doc_type is null or p_domain is null then raise_application_error(-20869,'RESERVATION_CONFLICT'); end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_cell,0,p_qty,p_uom,p_uom_version);
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_uid,p_cell,p_id);
  insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,
   SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,ARTICUL,QTY,UNIT_CODE,WARE_ID,CELL,UID_PALLET,
   STATUS,PRIORITY,CREATED_BY,BASE_QTY,BASE_UOM,RESERVATION_VERSION)
   values(p_id,'HARD','QTY',p_domain,p_doc_type,p_doc_id,p_line_id,v_article,p_qty,p_uom,v_ware,p_cell,p_uid,
   'ACTIVE',0,p_actor,p_qty,p_uom,0);
  if p_details is not null then
   v_details:=json_object_t.parse(p_details);
   if v_details.get_string('reservation_scope') is null or v_details.get_string('reservation_scope') not in('PALLET','QTY','CASE','BATCH','CELL') then raise_application_error(-20869,'RESERVATION_SCOPE_INVALID');end if;
   update RRL_STOCK_RESERVATION set RESERVATION_SCOPE=v_details.get_string('reservation_scope'),
    TASK_ID=v_details.get_number('task_id'),CUSTOMER_ID=v_details.get_number('customer_id'),CUSTOMER_ORDER_ID=v_details.get_number('customer_order_id'),
    PRODUCTION_ORDER_ID=case when p_doc_type='PRODUCTION_ORDER' then p_doc_id else v_details.get_number('production_order_id') end,
    PICK_PLAN_ID=case when p_doc_type='PICK_PLAN' then p_doc_id else v_details.get_number('pick_plan_id') end,
    PICK_PLAN_LINE_ID=v_details.get_number('pick_plan_line_id'),PICK_WAVE_ID=case when p_doc_type='PICK_WAVE' then p_doc_id else v_details.get_number('pick_wave_id') end,
    PICK_WAVE_LINE_ID=v_details.get_number('pick_wave_line_id'),BATCH_ID=v_details.get_string('batch_id'),PROD_BATCH_ID=v_details.get_number('prod_batch_id'),
    CELL_SLOT_ID=v_details.get_number('cell_slot_id'),PRIORITY=nvl(v_details.get_number('priority'),100),RESERVATION_VERSION=RESERVATION_VERSION+1
    where RESERVATION_ID=p_id;
  end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure release_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2) is r RRL_STOCK_RESERVATION%rowtype;
 begin
  check_owner(p_id,p_qty,p_doc_type,p_doc_id,r);
  RRL_STOCK_BALANCE_CORE.apply_delta(r.UID_PALLET,r.CELL,0,-p_qty,r.BASE_UOM,p_uom_version);
  decrease(r,p_qty,'RELEASED',p_actor);
 end;
 procedure consume_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2) is r RRL_STOCK_RESERVATION%rowtype;
 begin
  check_owner(p_id,p_qty,p_doc_type,p_doc_id,r);
  RRL_STOCK_BALANCE_CORE.apply_delta(r.UID_PALLET,r.CELL,-p_qty,-p_qty,r.BASE_UOM,p_uom_version);
  decrease(r,p_qty,'CONSUMED',p_actor);
 end;
 procedure relocate_hard(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
   p_qty number,p_uom_version number,p_actor varchar2) is
  r RRL_STOCK_RESERVATION%rowtype;v_art varchar2(160);v_ware number;
 begin
  lock_identity(p_id);lock_identity(p_new_id);
  select * into r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if r.RESERVATION_KIND!='HARD' or r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
   or r.BASE_QTY is null or p_qty is null or p_qty<=0 or r.BASE_QTY<p_qty then raise_application_error(-20869,'RESERVATION_CONFLICT'); end if;
  select ARTICUL into v_art from RRL_PALLETS where UID_PALLET=p_target_uid;
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_target_cell;
  if v_art!=r.ARTICUL then raise_application_error(-20869,'RESERVATION_ARTICLE_CONFLICT'); end if;
  -- Must accompany physical movement of the same q; source/destination P/H changed together.
  RRL_STOCK_BALANCE_CORE.apply_delta(r.UID_PALLET,r.CELL,-p_qty,-p_qty,r.BASE_UOM,p_uom_version);
  RRL_STOCK_BALANCE_CORE.apply_delta(p_target_uid,p_target_cell,p_qty,p_qty,r.BASE_UOM,p_uom_version);
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_target_uid,p_target_cell,p_new_id);
  insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,
   SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,TASK_ID,CUSTOMER_ID,CUSTOMER_ORDER_ID,PRODUCTION_ORDER_ID,
   PICK_PLAN_ID,PICK_PLAN_LINE_ID,PICK_WAVE_ID,PICK_WAVE_LINE_ID,ARTICUL,QTY,UNIT_CODE,WARE_ID,CELL,
   BATCH_ID,PROD_BATCH_ID,UID_PALLET,SSCC,STATUS,PRIORITY,CREATED_BY,BASE_QTY,BASE_UOM,RESERVATION_VERSION)
   values(p_new_id,'HARD',r.RESERVATION_SCOPE,r.RESERVATION_DOMAIN,r.SOURCE_DOC_TYPE,r.SOURCE_DOC_ID,
   r.SOURCE_LINE_ID,r.TASK_ID,r.CUSTOMER_ID,r.CUSTOMER_ORDER_ID,r.PRODUCTION_ORDER_ID,r.PICK_PLAN_ID,
   r.PICK_PLAN_LINE_ID,r.PICK_WAVE_ID,r.PICK_WAVE_LINE_ID,r.ARTICUL,p_qty,r.BASE_UOM,v_ware,p_target_cell,
   r.BATCH_ID,r.PROD_BATCH_ID,p_target_uid,null,r.STATUS,r.PRIORITY,p_actor,p_qty,r.BASE_UOM,0);
  RRL_STOCK_CTX_API.end_effect;
  decrease(r,p_qty,'CONSUMED',p_actor);
 end;
 procedure move_coverage(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
  p_target_ware number,p_qty number,p_target_slot number,p_actor varchar2,p_result_id out number) is
  v_r RRL_STOCK_RESERVATION%rowtype;v_new RRL_STOCK_RESERVATION%rowtype;
 begin
  lock_identity(p_id);
  select * into v_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if v_r.BASE_QTY is null or p_qty is null or p_qty<=0 or p_qty>v_r.BASE_QTY
   or v_r.RESERVATION_KIND is null or v_r.RESERVATION_KIND!='HARD'
   or v_r.STATUS is null or v_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
   or v_r.BASE_UOM is null then raise_application_error(-20869,'RESERVATION_COVERAGE_CONFLICT');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'STOCK_WRITE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_r.UID_PALLET));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_target_uid));
  if p_target_slot is not null then
   RRL_STOCK_LOCK_API.assert_held(40,RRL_STOCK_LOCK_API.resource_key('SLOT',to_char(p_target_slot,'TM9')));
  end if;
  if p_qty=v_r.BASE_QTY then
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_target_uid,p_target_cell,p_id);
   update RRL_STOCK_RESERVATION set UID_PALLET=p_target_uid,CELL=p_target_cell,WARE_ID=p_target_ware,
    CELL_SLOT_ID=p_target_slot,RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=p_id;
   RRL_STOCK_CTX_API.end_effect;
   p_result_id:=p_id;
  else
   lock_identity(p_new_id);v_new:=v_r;v_new.RESERVATION_ID:=p_new_id;
   v_new.UID_PALLET:=p_target_uid;v_new.CELL:=p_target_cell;v_new.WARE_ID:=p_target_ware;
   v_new.CELL_SLOT_ID:=p_target_slot;v_new.BASE_QTY:=p_qty;v_new.QTY:=p_qty;v_new.UNIT_CODE:=v_new.BASE_UOM;
   v_new.RESERVATION_VERSION:=0;v_new.CREATED_AT:=systimestamp;v_new.CREATED_BY:=p_actor;
   v_new.RELEASED_AT:=null;v_new.RELEASED_BY:=null;v_new.CONSUMED_AT:=null;v_new.CONSUMED_BY:=null;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_target_uid,p_target_cell,p_new_id);
   insert into RRL_STOCK_RESERVATION values v_new;
   RRL_STOCK_CTX_API.end_effect;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',v_r.UID_PALLET,v_r.CELL,p_id);
   update RRL_STOCK_RESERVATION set BASE_QTY=BASE_QTY-p_qty,QTY=BASE_QTY-p_qty,UNIT_CODE=BASE_UOM,
    RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=p_id;
   RRL_STOCK_CTX_API.end_effect;
   p_result_id:=p_new_id;
  end if;
 end;
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
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
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
  if v_kind='RESERVATION_CREATE' and m.get_string('reservation_kind')='SOFT' then
   v_qty:=RRL_STOCK_MATH.quantity(m.get_string('qty'));
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,v_id);
   insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,
    SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,ARTICUL,QTY,UNIT_CODE,STATUS,PRIORITY,CREATED_BY,RESERVATION_VERSION)
    values(v_id,'SOFT',m.get_string('reservation_scope'),m.get_string('reservation_domain'),v_type,v_doc,
     m.get_number('source_line_id'),v_article,v_qty,m.get_string('unit_code'),'ACTIVE',nvl(m.get_number('priority'),100),p_actor,0);
   RRL_STOCK_CTX_API.end_effect;
  elsif old.RESERVATION_KIND='SOFT' and v_kind in('RESERVATION_RELEASE','RESERVATION_CANCEL') then
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
     update RRL_STOCK_RESERVATION set RESERVATION_KIND='HARD',RESERVATION_SCOPE=m.get_string('reservation_scope'),
      UID_PALLET=v_uid,CELL=v_cell,WARE_ID=v_ware,QTY=v_qty,UNIT_CODE=v_base,BASE_QTY=v_qty,BASE_UOM=v_base,
      STATUS='ACTIVE',RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=v_id;
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

create or replace package body RRL_STOCK_TASK_CORE as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_meta json_object_t;v_source json_object_t;v_domain json_object_t;
  v_plan clob;v_task RRL_WAREHOUSE_TASK%rowtype;v_residual RRL_WAREHOUSE_TASK%rowtype;v_pallet RRL_PALLETS%rowtype;
  v_task_id number;v_qty number;v_original number;v_qbase number;v_target varchar2(200);v_base varchar2(20);
  v_factor_num number;v_factor_den number;v_scale number;v_version number;v_article varchar2(160);
  v_residual_id number;v_reservation number;v_new_reservation number;v_ware number;v_pick_task number;
  v_signature varchar2(64);v_hash varchar2(64);v_op varchar2(100);v_units clob;v_n number;v_doc_status varchar2(40);
  v_result json_object_t:=json_object_t();v_resource number;v_session number;v_equipment number;v_sync_id number;v_sync_key varchar2(400);v_session_actor varchar2(100);v_input_uom varchar2(20);v_source_p number;v_uom_signature varchar2(64);v_sap_header number;v_sap_cell varchar2(60);v_sap_ware number;
 begin
  v_doc.on_error(1);v_source:=v_doc.get_object('source');v_meta:=v_doc.get_object('metadata');v_meta.on_error(1);
  v_op:=v_doc.get_string('operation_id');v_task_id:=v_source.get_number('task_id');
  
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)));
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
  v_domain:=json_object_t.parse(v_plan).get_object('domain');
  -- Existing assignment/start commands lock the source document before the task.
  -- Read identity without a row lock, validate the planned signature, then use the same order.
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id;
  if nvl(v_meta.get_number('document_confirmation'),0)=1 then
   if v_task.TASK_SOURCE!='MES_RAW_SUPPLY' or RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_confirm')!=1 then raise_application_error(-20882,'MES_DOCUMENT_CONFIRM_FORBIDDEN');end if;
  elsif RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'TASK_COMPLETE_FORBIDDEN');end if;
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string('task_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: task source');end if;
  if v_task.TASK_SOURCE='WAVE' then
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update;
  elsif v_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update;
  elsif v_task.TASK_SOURCE='SAP_RECEIPT' then
   select NAKLAD_ID,RECEIVE_CELL,WARE_ID into v_sap_header,v_sap_cell,v_sap_ware from RRL_SAP_SUPPLY_ORDER where ORDER_ID=v_domain.get_string('sap_order_id') for update;
   if v_sap_header!=v_task.SOURCE_DOC_ID or v_sap_cell!=v_task.FROM_CELL or v_sap_ware!=v_domain.get_number('from_ware_id') then raise_application_error(-20890,'CLOSURE_CHANGED: putaway source order');end if;
   select to_char(CONDITION) into v_doc_status from RRL_PRIHOD_NAKLAD where ID=v_task.SOURCE_DOC_ID for update;
  end if;
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id for update;
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string('task_signature') then
   raise_application_error(-20890,'CLOSURE_CHANGED: task identity');
  end if;
  if v_task.STATUS is null or v_task.STATUS not in('PLANNED','ASSIGNED','IN_PROGRESS') then
   raise_application_error(-20886,'TASK_STATE_CONFLICT');end if;
  v_task.FROM_WARE_ID:=v_domain.get_number('from_ware_id');v_task.TO_WARE_ID:=v_domain.get_number('to_ware_id');
  if v_task.FROM_WARE_ID is null or v_task.TO_WARE_ID is null or (v_task.FROM_WARE_ID!=v_task.TO_WARE_ID and v_task.TASK_SOURCE not in('MES_RAW_SUPPLY','MES_COMPLETION')) then
   raise_application_error(-20886,'INTERWAREHOUSE_COMMAND_REQUIRED');end if;
  if nvl(v_meta.get_number('document_confirmation'),0)!=1 and (upper(trim(v_meta.get_string('scanned_pallet'))) is null or
   trim(v_meta.get_string('scanned_pallet')) not in(nvl(v_task.UID_PALLET,v_task.SSCC),nvl(v_task.SSCC,v_task.UID_PALLET))
   or upper(trim(v_meta.get_string('scanned_from_cell'))) is null or upper(trim(v_meta.get_string('scanned_from_cell')))!=upper(v_task.FROM_CELL)
   or upper(trim(v_meta.get_string('scanned_to_cell'))) is null or upper(trim(v_meta.get_string('scanned_to_cell')))!=upper(v_task.TO_CELL)) then
   raise_application_error(-20886,'TASK_SCAN_CONFLICT');end if;
  v_original:=v_task.QTY;v_qty:=v_original;
  if v_meta.has('fact_qty') and not v_meta.get('fact_qty').is_null then v_qty:=RRL_STOCK_MATH.quantity(v_meta.get_string('fact_qty'));end if;
  if v_qty is null or v_qty<=0 or v_qty>v_original or (v_task.QTY_MODE='PALLET' and v_qty!=v_original) then
   raise_application_error(-20886,'TASK_QUANTITY_CONFLICT');end if;
  v_target:=v_domain.get_string('target_uid');v_residual_id:=v_domain.get_number('residual_task_id');
  v_reservation:=v_domain.get_number('source_reservation_id');v_new_reservation:=v_domain.get_number('new_reservation_id');
  v_pick_task:=v_domain.get_number('pick_task_id');
  select * into v_pallet from RRL_PALLETS where UID_PALLET=nvl(v_task.UID_PALLET,v_task.SSCC);
  v_article:=v_pallet.ARTICUL;
  if (v_task.RAW_ARTICUL is not null and v_task.RAW_ARTICUL!=v_article) or (v_task.TARGET_ARTICUL is not null and v_task.TARGET_ARTICUL!=v_article) then raise_application_error(-20887,'TASK_ARTICLE_CONFLICT');end if;
  select BASE_UOM,REMAIN into v_input_uom,v_source_p from RRL_REMAINS where UID_POLETA=v_pallet.UID_PALLET and CELL=v_task.FROM_CELL;
  v_input_uom:=nvl(v_task.UNIT_CODE,v_input_uom);
  RRL_STOCK_PALLET_UOM.resolve_quantity(v_pallet.UID_PALLET,v_input_uom,RRL_STOCK_PLAN_HELPER.decimal_text(v_qty),
   v_base,v_qbase,v_version,v_uom_signature);
  if v_uom_signature!=v_domain.get_string('uom_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: pallet pack');end if;
  if v_version!=v_domain.get_number('uom_version') or RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase)!=v_domain.get_string('base_quantity') or RRL_STOCK_PLAN_HELPER.decimal_text(v_source_p)!=v_domain.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: task quantity policy');end if;
  if v_task.QTY_MODE='PALLET' and v_qbase!=v_source_p then raise_application_error(-20886,'WHOLE_PALLET_STOCK_CHANGED');end if;
  if v_task.TASK_SOURCE='WAVE' then
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update;
   if v_doc_status='CANCELLED' then raise_application_error(-20886,'SOURCE_DOCUMENT_CANCELLED');end if;
  elsif v_task.TASK_SOURCE='SAP_RECEIPT' then
   if v_qty!=v_original then raise_application_error(-20886,'PUTAWAY_MUST_BE_WHOLE');end if;
   select count(*) into v_n from RRL_SAP_PALLET_RECEIPT rec join RRL_SAP_SUPPLY_ORDER so on so.ORDER_ID=rec.ORDER_ID
    where rec.UID_PALLET=v_pallet.UID_PALLET and so.NAKLAD_ID=v_task.SOURCE_DOC_ID and so.RECEIVE_CELL=v_task.FROM_CELL and so.WARE_ID=v_task.FROM_WARE_ID;
   if v_n!=1 then raise_application_error(-20886,'PUTAWAY_RECEIPT_SOURCE_CONFLICT');end if;
   if v_task.TO_CELL_SLOT_ID is not null then
    select count(*) into v_n from RRL_RECEIPT_SLOT_CLAIM cl join RRL_TOPOLOGY_CELL_SLOT sl on sl.CELL_SLOT_ID=cl.CELL_SLOT_ID
     where cl.TASK_ID=v_task_id and cl.STATUS='RESERVED' and sl.ACTIVE=1;
    if v_n!=1 then raise_application_error(-20886,'PUTAWAY_SLOT_CONFLICT');end if;
   end if;
  elsif v_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER
    where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update;
   if v_doc_status='CANCELLED' then raise_application_error(-20886,'SOURCE_DOCUMENT_CANCELLED');end if;
  else raise_application_error(-20888,'TASK_DOMAIN_HANDLER_REQUIRED');end if;
  if v_target!=v_pallet.UID_PALLET then
   RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','PALLET:'||v_target));
   v_pallet.STOCK_ORIGIN_UID:=nvl(v_pallet.STOCK_ORIGIN_UID,v_pallet.UID_PALLET);v_pallet.CREATED_BY_STOCK_OP:=v_op;
   if v_pallet.WEIGHT_BRUTTO is not null then
    if v_pallet.UNIT_COUNT is null or v_pallet.UNIT_COUNT<=0 then raise_application_error(-20887,'PALLET_BIRTH_QUANTITY_REQUIRED');end if;
    v_pallet.WEIGHT_BRUTTO:=v_pallet.WEIGHT_BRUTTO*v_qbase/v_pallet.UNIT_COUNT;
   end if;
   v_pallet.UID_PALLET:=v_target;v_pallet.SSCC:=null;v_pallet.UNIT_COUNT:=v_qbase;v_pallet.PRINTED:=0;
   insert into RRL_PALLETS values v_pallet;
  end if;
  if v_meta.has('unit_keys') and v_meta.get_array('unit_keys').get_size>0 then v_units:=v_meta.get_array('unit_keys').to_clob;end if;
  RRL_STOCK_TRANSFER_CORE.move(nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,
   v_qbase,v_base,v_version,v_task.TO_WARE_ID,p_actor,1,v_reservation,v_units,v_new_reservation,v_task.TO_CELL_SLOT_ID,v_task.FROM_WARE_ID,case when v_task.TASK_SOURCE='SAP_RECEIPT' then 'PUTAWAY' else 'ORDINARY' end);
  v_resource:=v_meta.get_number('resource_id');v_session:=v_meta.get_number('resource_session_id');v_equipment:=v_meta.get_number('equipment_id');
  if v_session is not null then
   select RESOURCE_ID,EQUIPMENT_ID,OPERATOR_USER_ID into v_resource,v_equipment,v_session_actor from RRL_RESOURCE_SESSION where SESSION_ID=v_session and STATUS='ACTIVE' for update;
   if v_session_actor is null or v_session_actor!=p_actor then raise_application_error(-20882,'TASK_SESSION_OWNER_CONFLICT');end if;
  end if;
  v_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  if v_residual_id is not null then
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_residual_id)));
   v_residual:=v_task;v_residual.TASK_ID:=v_residual_id;v_residual.QTY:=v_original-v_qty;
   v_residual.PARENT_TASK_ID:=v_task_id;v_residual.STATUS:='PLANNED';v_residual.FACT_QTY:=null;
   v_residual.CREATED_BY:=p_actor;v_residual.CREATED_AT:=systimestamp;v_residual.COMPLETION_HASH:=null;
   v_residual.COMPLETION_JSON:=null;v_residual.FINISHED_AT:=null;v_residual.ASSIGNED_TO:=null;
   v_residual.STARTED_AT:=null;v_residual.TARGET_UID_PALLET:=null;v_residual.LAST_ERROR:='Residual of task '||v_task_id;
   insert into RRL_WAREHOUSE_TASK values v_residual;
  end if;
  update RRL_WAREHOUSE_TASK set STATUS='DONE',QTY=v_qty,FACT_QTY=v_qty,TARGET_UID_PALLET=v_target,
   FROM_WARE_ID=v_task.FROM_WARE_ID,TO_WARE_ID=v_task.TO_WARE_ID,FINISHED_AT=systimestamp,ASSIGNED_TO=p_actor,RESOURCE_ID=nvl(v_resource,RESOURCE_ID),
   RESOURCE_SESSION_ID=nvl(v_session,RESOURCE_SESSION_ID),EQUIPMENT_ID=nvl(v_equipment,EQUIPMENT_ID),
   COMPLETION_HASH=v_hash,COMPLETION_JSON=p_request,LAST_ERROR=null where TASK_ID=v_task_id;
  insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,
   SOURCE_TASK_ID,UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY)
   values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,v_task_id,v_task.TASK_SOURCE,v_task.TASK_TYPE,v_task.SOURCE_DOC_TYPE,v_task.SOURCE_DOC_ID,
    v_task.SOURCE_TASK_ID,nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,v_qty,v_qbase,v_base,v_op,systimestamp,p_actor);
  if v_resource is not null or v_session is not null or v_equipment is not null then
   insert into RRL_RESOURCE_FACT_EVENT(EVENT_ID,TASK_ID,SESSION_ID,RESOURCE_ID,EVENT_TYPE,EVENT_AT,EVENT_BY,PAYLOAD_JSON)
    values(RRL_RESOURCE_FACT_EVENT_SQ.nextval,v_task_id,v_session,v_resource,'COMPLETED',systimestamp,p_actor,p_request);
  end if;
  RRL_STOCK_TASK_DOMAIN.sync_fact(v_task,v_qty,v_target,v_residual_id,p_actor);
  v_sync_id:=v_domain.get_number('sync_id');v_sync_key:=v_domain.get_string('sync_key');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id)));
  merge into RRL_WAREHOUSE_TASK_SYNC d using(select v_sync_key SYNC_KEY from dual)s on(d.SYNC_KEY=s.SYNC_KEY)
   when matched then update set d.SYNC_STATUS='SYNCED',d.SYNCED_AT=systimestamp,d.UPDATED_AT=systimestamp,d.UPDATED_BY=p_actor,d.LAST_ERROR=null
   when not matched then insert(SYNC_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,SOURCE_MOVEMENT_ID,SYNC_KEY,SYNC_STATUS,SYNC_ATTEMPT,CREATED_AT,UPDATED_AT,SYNCED_AT,UPDATED_BY)
    values(v_sync_id,v_task_id,v_task.TASK_SOURCE,v_task.TASK_TYPE,v_task.SOURCE_DOC_TYPE,v_task.SOURCE_DOC_ID,v_task.SOURCE_TASK_ID,v_task.SOURCE_MOVEMENT_ID,v_sync_key,'SYNCED',1,systimestamp,systimestamp,systimestamp,p_actor);
  v_result.put('operation_id',v_op);v_result.put('task_id',v_task_id);v_result.put('status','DONE');
  v_result.put('pallet_identifier',v_target);v_result.put('source_pallet_identifier',nvl(v_task.UID_PALLET,v_task.SSCC));
  v_result.put('cell',v_task.TO_CELL);v_result.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
  v_result.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase));v_result.put('base_uom',v_base);
  v_result.put('residual_task_id',v_residual_id);v_result.put('movement_id',v_domain.get_number('new_movement_id'));p_result:=v_result.to_clob;
  if v_task.TASK_SOURCE='SAP_RECEIPT' then
   v_result.put('order_id',v_domain.get_string('sap_order_id'));v_result.put('line_number',v_domain.get_string('sap_line_number'));
   v_result.put('article',v_article);p_result:=v_result.to_clob;
   insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)
    values('PUTAWAY:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id),'PALLET_PUTAWAY',p_result);
  end if;
 end;
end;
/
