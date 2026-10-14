create or replace package RRL_STOCK_RESERVE_CORE authid definer
 accessible by(package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_TRANSFER_CORE) as
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
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2,p_details clob default null) is v_article varchar2(160);v_ware number;v_details json_object_t;v_carrier number;
 begin
  lock_identity(p_id);
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  select count(*) into v_carrier from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
  if v_carrier>0 then raise_application_error(-20869,'CASE_CARRIER_NOT_ALLOCATABLE: unpack through carrier return');end if;
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
   if v_details.get_string('reservation_scope') is null or v_details.get_string('reservation_scope') not in('PALLET','QTY') then raise_application_error(-20869,'RESERVATION_SCOPE_INVALID');end if;
   declare
 v_json_sql_1_1 varchar2(32767):=v_details.get_string('reservation_scope');
 v_json_sql_1_2 number:=v_details.get_number('task_id');
 v_json_sql_1_3 number:=v_details.get_number('customer_id');
 v_json_sql_1_4 number:=v_details.get_number('customer_order_id');
 v_json_sql_1_5 number:=v_details.get_number('production_order_id');
 v_json_sql_1_6 number:=v_details.get_number('pick_plan_id');
 v_json_sql_1_7 number:=v_details.get_number('pick_plan_line_id');
 v_json_sql_1_8 number:=v_details.get_number('pick_wave_id');
 v_json_sql_1_9 number:=v_details.get_number('pick_wave_line_id');
 v_json_sql_1_10 varchar2(32767):=v_details.get_string('batch_id');
 v_json_sql_1_11 number:=v_details.get_number('prod_batch_id');
 v_json_sql_1_12 number:=v_details.get_number('cell_slot_id');
 v_json_sql_1_13 number:=v_details.get_number('priority');
begin
update RRL_STOCK_RESERVATION set RESERVATION_SCOPE=v_json_sql_1_1,
    TASK_ID=v_json_sql_1_2,CUSTOMER_ID=v_json_sql_1_3,CUSTOMER_ORDER_ID=v_json_sql_1_4,
    PRODUCTION_ORDER_ID=case when p_doc_type='PRODUCTION_ORDER' then p_doc_id else v_json_sql_1_5 end,
    PICK_PLAN_ID=case when p_doc_type='PICK_PLAN' then p_doc_id else v_json_sql_1_6 end,
    PICK_PLAN_LINE_ID=v_json_sql_1_7,PICK_WAVE_ID=case when p_doc_type='PICK_WAVE' then p_doc_id else v_json_sql_1_8 end,
    PICK_WAVE_LINE_ID=v_json_sql_1_9,BATCH_ID=v_json_sql_1_10,PROD_BATCH_ID=v_json_sql_1_11,
    CELL_SLOT_ID=v_json_sql_1_12,PRIORITY=nvl(v_json_sql_1_13,100),RESERVATION_VERSION=RESERVATION_VERSION+1
    where RESERVATION_ID=p_id;
end;
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

create or replace package RRL_STOCK_WAVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_reserve(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_WAVE_CMD as
 function signature(p_row RRL_PICK_WAVE_REPLENISH_TASK%rowtype) return varchar2 is v json_object_t:=json_object_t();
 begin
  v.put('id',p_row.PICK_WAVE_REPLENISH_TASK_ID);v.put('wave',p_row.PICK_WAVE_ID);v.put('article',p_row.ARTICUL);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_row.QTY));v.put('target',p_row.TARGET_CELL_CODE);
  v.put('scope',p_row.REPLENISHMENT_QTY_MODE);v.put('shelf_days',p_row.MIN_SHELF_LIFE_DAYS);v.put('shelf_percent',p_row.MIN_SHELF_LIFE_PERCENT);
  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v_wave number;v_ware number;v_id number;v_qty number;v_version number;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;
  v_uid varchar2(200);v_cell varchar2(60);v_uom varchar2(20);v_free number;v_own_id number;v_own_qty number;v_num number;v_den number;v_scale number;
  type quantities is table of number index by varchar2(2000);used quantities;k varchar2(2000);
 begin
  v_wave:=d.get_object('source').get_number('wave_id');select WARE_ID into v_ware from RRL_PICK_WAVE where PICK_WAVE_ID=v_wave;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v_wave));
  for rt in(select * from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=v_wave
   and STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX') and SOURCE_RESERVATION_ID is null order by PICK_WAVE_REPLENISH_TASK_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'WAVE_RESERVATION_BATCH_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(rt.PICK_WAVE_REPLENISH_TASK_ID));
   RRL_STOCK_PLAN_HELPER.fence(f,'SKU',rt.ARTICUL);
   v_uid:=null;v_qty:=null;v_cell:=null;v_uom:=null;v_version:=null;
   v_own_id:=null;v_own_qty:=null;
   for own in(select sr.RESERVATION_ID,sr.BASE_QTY,sr.UID_PALLET,sr.CELL,sr.BASE_UOM,rr.REMAIN
    from RRL_STOCK_RESERVATION sr join RRL_REMAINS rr on rr.UID_POLETA=sr.UID_PALLET and rr.CELL=sr.CELL
    join RRL_CELLS cc on cc.CELL=sr.CELL
    where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=v_wave and sr.SOURCE_LINE_ID=rt.PICK_TASK_ID
     and sr.RESERVATION_DOMAIN='PICKING' and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')
     and sr.BASE_QTY>=rt.QTY and cc.WARE_ID=v_ware and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0
    order by sr.RESERVATION_ID) loop
    v_own_id:=own.RESERVATION_ID;v_own_qty:=own.BASE_QTY;v_uid:=own.UID_PALLET;v_cell:=own.CELL;v_uom:=own.BASE_UOM;
    v_qty:=case when rt.REPLENISHMENT_QTY_MODE='FULL_PALLET' then own.REMAIN else rt.QTY end;
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=rt.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
    if v_version is null then raise_application_error(-20868,'WAVE_BASE_POLICY_REQUIRED');end if;
    exit;
   end loop;
   if v_own_id is null then
   for c in(select rr.UID_POLETA,rr.CELL,rr.REMAIN,rr.HARD_RESERVED_BASE,rr.BASE_UOM,pp.EXPIRY_DATE,pp.PRODUCED_DATE
    from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA join RRL_CELLS cc on cc.CELL=rr.CELL
    where pp.ARTICUL=rt.ARTICUL and rr.REMAIN>rr.HARD_RESERVED_BASE and cc.WARE_ID=v_ware
     and rr.CELL!=rt.TARGET_CELL_CODE and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0
     and (rt.MIN_SHELF_LIFE_DAYS is null or trunc(pp.EXPIRY_DATE)-trunc(sysdate)>=rt.MIN_SHELF_LIFE_DAYS)
     and (rt.MIN_SHELF_LIFE_PERCENT is null or (pp.PRODUCED_DATE is not null and pp.EXPIRY_DATE>pp.PRODUCED_DATE
      and (trunc(pp.EXPIRY_DATE)-trunc(sysdate))*100 >= rt.MIN_SHELF_LIFE_PERCENT*(trunc(pp.EXPIRY_DATE)-trunc(pp.PRODUCED_DATE))))
    order by pp.EXPIRY_DATE nulls last,pp.PRODUCED_DATE nulls last,rr.CELL,rr.UID_POLETA
   ) loop
    k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA,c.CELL));if not used.exists(k) then used(k):=0;end if;
    v_free:=c.REMAIN-c.HARD_RESERVED_BASE-used(k);
    if v_free>=rt.QTY and (nvl(rt.REPLENISHMENT_QTY_MODE,'PARTIAL')!='FULL_PALLET' or c.HARD_RESERVED_BASE+used(k)=0) then
     v_uid:=c.UID_POLETA;v_cell:=c.CELL;v_uom:=c.BASE_UOM;
     v_qty:=case when rt.REPLENISHMENT_QTY_MODE='FULL_PALLET' then c.REMAIN else rt.QTY end;
     select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=rt.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
     if v_version is null then raise_application_error(-20868,'WAVE_BASE_POLICY_REQUIRED');end if;
     used(k):=used(k)+v_qty;exit;
    end if;
   end loop;
   end if;
   x:=json_object_t();x.put('own_reservation_id',v_own_id);x.put('own_qty',case when v_own_qty is not null then RRL_STOCK_PLAN_HELPER.decimal_text(v_own_qty) end);x.put('task_id',rt.PICK_WAVE_REPLENISH_TASK_ID);x.put('signature',signature(rt));x.put('uid',v_uid);
   if v_uid is not null then
    if v_own_id is null then select RRL_STOCK_RESERVATION_SQ.nextval into v_id from dual;else v_id:=v_own_id;end if;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_uid,rt.ARTICUL,v_cell,null);
    x.put('reservation_id',v_id);x.put('cell',v_cell);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));x.put('base_uom',v_uom);x.put('uom_version',v_version);
   end if;
   a.append(x);
  end loop;
  v.put('wave_id',v_wave);v.put('warehouse',v_ware);v.put('tasks',a);p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_reserve(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();
  a json_array_t;v_plan clob;v_status varchar2(40);rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype;
  v_qty number;v_id number;v_units clob;v_count number:=0;v_details json_object_t;v_produced date;v_expiry date;own RRL_STOCK_RESERVATION%rowtype;
 begin
  if RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')!=1 and RRL_HAS_WRIGHT(p_actor,'pick_wave_release_reserves')!=1 then raise_application_error(-20882,'WAVE_RESERVATION_FORBIDDEN');end if;
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;
end;
  v:=json_object_t.parse(v_plan).get_object('domain');a:=v.get_array('tasks');
  declare
 v_json_sql_2_1 number:=v.get_number('wave_id');
begin
select STATUS into v_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_json_sql_2_1 for update;
end;
  if v_status in('CANCELLED','COMPLETED','CLOSED') then raise_application_error(-20886,'WAVE_NOT_OPEN');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   declare
 v_json_sql_3_1 number:=x.get_number('task_id');
begin
select * into rt from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=v_json_sql_3_1 for update;
end;
   if rt.SOURCE_RESERVATION_ID is not null or signature(rt)!=x.get_string('signature') or rt.STATUS not in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX') then raise_application_error(-20890,'CLOSURE_CHANGED: replenishment row');end if;
   if x.get('uid').is_null then
    update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='FAILED',WAIT_REASON='No eligible source stock',UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;
   else
    v_qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));v_id:=x.get_number('reservation_id');
    if x.get('own_reservation_id').is_null then
    v_units:=RRL_STOCK_UNIT_CORE.automatic_units(x.get_string('uid'),x.get_string('cell'),v_qty);
    v_details:=json_object_t();v_details.put('pick_wave_id',v.get_number('wave_id'));
    v_details.put('reservation_scope',case when rt.REPLENISHMENT_QTY_MODE='FULL_PALLET' then 'PALLET' else 'QTY' end);
    RRL_STOCK_RESERVE_CORE.create_hard(v_id,x.get_string('uid'),x.get_string('cell'),v_qty,x.get_string('base_uom'),x.get_number('uom_version'),
     'PICK_WAVE',v.get_number('wave_id'),rt.PICK_WAVE_REPLENISH_TASK_ID,'WAVE',p_actor,v_details.to_clob);
    RRL_STOCK_UNIT_CORE.reserve_units(x.get_string('uid'),x.get_string('cell'),v_id,v_qty,v_units);
    else
     select * into own from RRL_STOCK_RESERVATION where RESERVATION_ID=v_id for update;
     if own.SOURCE_DOC_TYPE!='PICK_WAVE' or own.SOURCE_DOC_ID!=v.get_number('wave_id') or own.SOURCE_LINE_ID!=rt.PICK_TASK_ID
      or own.RESERVATION_DOMAIN!='PICKING' or own.RESERVATION_KIND!='HARD' or own.STATUS not in('ACTIVE','ALLOCATED','PICKING')
      or own.UID_PALLET!=x.get_string('uid') or own.CELL!=x.get_string('cell') or RRL_STOCK_PLAN_HELPER.decimal_text(own.BASE_QTY)!=x.get_string('own_qty') then
      raise_application_error(-20890,'CLOSURE_CHANGED: own picking reserve');end if;
    end if;
    declare
 v_json_sql_4_1 varchar2(32767):=x.get_string('uid');
begin
select PRODUCED_DATE,EXPIRY_DATE into v_produced,v_expiry from RRL_PALLETS where UID_PALLET=v_json_sql_4_1;
end;
    declare
 v_json_sql_5_1 varchar2(32767):=x.get_string('uid');
 v_json_sql_5_2 varchar2(32767):=x.get_string('cell');
begin
update RRL_PICK_WAVE_REPLENISH_TASK set SOURCE_RESERVATION_ID=v_id,PALLET_UID=v_json_sql_5_1,SOURCE_CELL_CODE=v_json_sql_5_2,
     SOURCE_AVAILABLE_QTY=v_qty,SOURCE_PRODUCED_DATE=v_produced,SOURCE_EXPIRY_DATE=v_expiry,QTY=v_qty,WAIT_REASON=null,UPDATED_AT=sysdate,UPDATED_BY=p_actor
     where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;
end;
    v_count:=v_count+1;
   end if;
  end loop;
  j.put('operation_id',d.get_string('operation_id'));j.put('wave_id',v.get_number('wave_id'));j.put('reserved_count',v_count);p_result:=j.to_clob;
 end;
end;
/

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

create or replace package RRL_STOCK_CASE_PICK_CMD authid definer
 accessible by(package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_POSTING_API) as
 function carrier_rows(p_task number) return clob;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_CASE_PICK_CMD as
 function carrier_rows(p_task number) return clob is
  a json_array_t:=json_array_t();x json_object_t;
 begin
  for r in(select h.LOT_UID,s.CELL,s.REMAIN,s.STOCK_VERSION,s.BASE_UOM,p.ARTICUL,h.CASE_PICK_LINE_ID
   from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID
   where h.CASE_PICK_TASK_ID=p_task and s.REMAIN>0 order by h.LOT_UID,s.CELL fetch first 201 rows only) loop
   if a.get_size=200 then raise_application_error(-20881,'CASE_CARRIER_LOT_BOUND');end if;
   x:=json_object_t();x.put('uid',r.LOT_UID);x.put('cell',r.CELL);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.REMAIN));
   x.put('version',r.STOCK_VERSION);x.put('base',r.BASE_UOM);x.put('article',r.ARTICUL);x.put('case_line',r.CASE_PICK_LINE_ID);a.append(x);
  end loop;
  return a.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;chunks json_array_t:=json_array_t();x json_object_t;selected_wire clob;
  ct RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;pt RRL_PICK_TASK%rowtype;
  task_id number;line_id number;fact number;remaining number;q number;basever number;newres number;target varchar2(150);n number:=0;v_cell varchar2(60);target_cell varchar2(60);
  type source_numbers is table of number index by varchar2(150);consumed source_numbers;steps source_numbers;
 begin
  task_id:=d.get_object('source').get_number('case_task_id');line_id:=d.get_object('source').get_number('case_line_id');
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id and CASE_PICK_TASK_ID=task_id;
  select * into pt from RRL_PICK_TASK where PICK_TASK_ID=l.PICK_TASK_ID;
  if ct.WARE_ID is null or ct.WARE_ID<1 or ct.SSCC is null or l.CELL_CODE is null or l.ARTICUL is null or l.PICK_TASK_ID is null or l.PICK_WAVE_TASK_ID is null or l.CUSTOMER_ORDER_ID is null then raise_application_error(-20887,'CASE_TASK_IDENTITY_REQUIRED');end if;
  fact:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'));remaining:=fact-nvl(l.PICKED_QTY,0);v_cell:=l.CELL_CODE;target_cell:='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(ct.WARE_ID);
  if remaining<=0 or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_NOT_INCREASING_OR_EXCEEDS_PLAN');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(line_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(l.CUSTOMER_ORDER_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  a:=json_array_t.parse(carrier_rows(task_id));
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),target_cell);
  end loop;
  selected_wire:=d.get_array('units').to_clob;
  for sr in(select sr.RESERVATION_ID,sr.UID_PALLET,sr.CELL,sr.BASE_QTY,sr.BASE_UOM,s.REMAIN,s.STOCK_VERSION,p.EXPIRY_DATE
   from RRL_STOCK_RESERVATION sr join RRL_REMAINS s on s.UID_POLETA=sr.UID_PALLET and s.CELL=sr.CELL
    join RRL_PALLETS p on p.UID_PALLET=sr.UID_PALLET
   where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=l.PICK_WAVE_ID and sr.SOURCE_LINE_ID=l.PICK_TASK_ID
    and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.CELL=v_cell
    and p.ARTICUL=l.ARTICUL and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET)
   order by p.EXPIRY_DATE nulls last,sr.UID_PALLET,sr.RESERVATION_ID fetch first 201 rows only) loop
   exit when remaining=0;n:=n+1;
   if n>200 or sr.BASE_QTY is null or sr.BASE_QTY<=0 then raise_application_error(-20881,'CASE_SOURCE_RESERVATION_BOUND_OR_INVALID');end if;
   if d.get_array('units').get_size>0 then
    select nvl(sum(u.BASE_QTY),0) into q from RRL_WMS_RECEIPT_UNIT u
     join json_table(selected_wire,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY
     where u.CURRENT_UID=sr.UID_PALLET and u.CURRENT_CELL=v_cell and u.HARD_RESERVATION_ID=sr.RESERVATION_ID and u.STOCK_STATUS!='ISSUED';
    if q=0 then continue;end if;
    if q>remaining or q>sr.BASE_QTY then raise_application_error(-20884,'CASE_SCANNED_UNIT_QUANTITY_CONFLICT');end if;
   else q:=least(remaining,sr.BASE_QTY);end if;
   remaining:=remaining-q;
   select max(POLICY_VERSION) into basever from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
   if basever is null then raise_application_error(-20868,'CASE_BASE_POLICY_REQUIRED');end if;
   target:='CASELOT:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256))||':'||RRL_STOCK_PLAN_HELPER.decimal_text(n);
   select RRL_STOCK_RESERVATION_SQ.nextval into newres from dual;
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.UID_PALLET,l.ARTICUL,v_cell,target_cell);
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',target);RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',target);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(newres));
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||target);
   x:=json_object_t();x.put('source_uid',sr.UID_PALLET);x.put('target_uid',target);x.put('reservation',sr.RESERVATION_ID);x.put('new_reservation',newres);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(q));x.put('base',sr.BASE_UOM);x.put('policy',basever);
   if not consumed.exists(sr.UID_PALLET) then consumed(sr.UID_PALLET):=0;steps(sr.UID_PALLET):=0;end if;
   x.put('stock_version',sr.STOCK_VERSION+steps(sr.UID_PALLET));x.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(sr.REMAIN-consumed(sr.UID_PALLET)));
   consumed(sr.UID_PALLET):=consumed(sr.UID_PALLET)+q;steps(sr.UID_PALLET):=steps(sr.UID_PALLET)+1;chunks.append(x);
  end loop;
  if remaining!=0 then raise_application_error(-20869,'CASE_OWN_HARD_IN_PICK_CELL_INSUFFICIENT');end if;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v.put('task_id',task_id);v.put('line_id',line_id);v.put('pick_task',l.PICK_TASK_ID);v.put('wave_task',l.PICK_WAVE_TASK_ID);
  v.put('wave_id',l.PICK_WAVE_ID);v.put('customer_order',l.CUSTOMER_ORDER_ID);v.put('warehouse',ct.WARE_ID);v.put('cell',v_cell);v.put('transit_cell',target_cell);v.put('article',l.ARTICUL);
  v.put('previous_qty',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(l.PICKED_QTY,0)));v.put('planned_qty',RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY));
  v.put('content_version',ct.CONTENT_VERSION);v.put('carrier_identifier',ct.SSCC);v.put('carrier',a);v.put('chunks',chunks);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;x json_object_t;
  a json_array_t;chunks json_array_t;facts json_array_t:=json_array_t();factx json_object_t;keys json_array_t;selected json_array_t;keyx json_element_t;unit_wire clob;
  ct RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;pt RRL_PICK_TASK%rowtype;p RRL_PALLETS%rowtype;
  plan clob;nowrows clob;oldrows clob;op varchar2(100);task_id number;line_id number;ware number;v_cell varchar2(60);article varchar2(160);target_cell varchar2(60);
  qty number;fact number;before_qty number;ver number;stockver number;physical number;owned number;base varchar2(20);uid varchar2(150);target varchar2(150);sid number;new_sid number;
  wave_status varchar2(40);n number;posted number;line_no number:=0;unit_key varchar2(64);matched number;scan_product varchar2(4000);newstatus varchar2(20);eventid number;offline varchar2(100);
 begin
  if RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 then raise_application_error(-20882,'CASE_PICK_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  task_id:=v.get_number('task_id');line_id:=v.get_number('line_id');ware:=v.get_number('warehouse');v_cell:=v.get_string('cell');article:=v.get_string('article');target_cell:=v.get_string('transit_cell');
  declare
 v_json_sql_1_1 number:=v.get_number('wave_id');
begin
select STATUS into wave_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_json_sql_1_1 for update;
end;
  if wave_status in('CANCELLED','CLOSED','DRAFT','PREVIEW') or wave_status is null then raise_application_error(-20886,'CASE_WAVE_STATE_CONFLICT');end if;
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id for update;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id for update;
  select * into pt from RRL_PICK_TASK where PICK_TASK_ID=l.PICK_TASK_ID for update;
  if ct.WARE_ID!=ware or ct.CONTENT_VERSION!=v.get_number('content_version') or ct.SSCC!=v.get_string('carrier_identifier')
   or l.CASE_PICK_TASK_ID!=task_id or l.PICK_TASK_ID!=v.get_number('pick_task') or l.PICK_WAVE_TASK_ID!=v.get_number('wave_task')
   or l.PICK_WAVE_ID!=v.get_number('wave_id') or l.CUSTOMER_ORDER_ID!=v.get_number('customer_order') or l.CELL_CODE!=v_cell or l.ARTICUL!=article
   or RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY)!=v.get_string('planned_qty')
   or RRL_STOCK_PLAN_HELPER.decimal_text(nvl(l.PICKED_QTY,0))!=v.get_string('previous_qty') then raise_application_error(-20890,'CLOSURE_CHANGED: case task identity');end if;
  if ct.STATUS is null or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT') or l.STATUS is null or l.STATUS not in('NEW','ACTIVE','SKIPPED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')
   or pt.TASK_TYPE is null or pt.TASK_TYPE!='CASE_PICK' or pt.STATUS is null or pt.STATUS in('DONE','CANCELLED','FAILED') or pt.CUSTOMER_ORDER_ID!=l.CUSTOMER_ORDER_ID or pt.ARTICUL!=article then raise_application_error(-20886,'CASE_TASK_LINE_STATE_CONFLICT');end if;
  -- Reporting/rejecting a short uses CONFIG exclusive; this command holds CONFIG shared
  -- and the same task/line anchors, so the pending decision cannot change this fact mid-post.
  select count(*) into n from RRL_CASE_PICK_SHORT where CASE_PICK_LINE_ID=line_id
   and STATUS in('CREATED','PENDING_APPROVAL');
  if n>0 then raise_application_error(-20886,'CASE_SHORT_DECISION_PENDING');end if;
  if ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=p_actor and RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'CASE_TASK_ACTOR_CONFLICT');end if;
  if m.get_string('scan_cell') is null or upper(m.get_string('scan_cell'))!=upper(v_cell)
   or m.get_string('scan_container') is null or m.get_string('scan_container')!=ct.SSCC then raise_application_error(-20886,'CASE_CELL_CARRIER_SCAN_REQUIRED');end if;
  scan_product:=m.get_string('scan_product');
  select count(*) into n from RRL_ARTICULS where ACTICUL=article and scan_product in(ACTICUL,BARCODE_SHT,BARCODE_KOR,BARCODE_BL);
  if n!=1 and d.get_array('units').get_size=0 then raise_application_error(-20886,'CASE_PRODUCT_SCAN_CONFLICT');end if;
  nowrows:=carrier_rows(task_id);a:=v.get_array('carrier');oldrows:=a.to_clob;
  if dbms_lob.compare(nowrows,oldrows)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: case carrier stock');end if;
  before_qty:=nvl(l.PICKED_QTY,0);posted:=0;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if x.get_number('case_line')=line_id then posted:=posted+RRL_STOCK_MATH.quantity(x.get_string('quantity'));end if;
  end loop;
  if posted!=before_qty then raise_application_error(-20886,'CASE_PRIOR_FACT_WITHOUT_PHYSICAL_POSTING');end if;
  fact:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'));
  if fact<=before_qty or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_CONFLICT');end if;
  keys:=d.get_array('units');unit_wire:=keys.to_clob;matched:=0;
  -- Move already picked contents with their carrier to the newly scanned pick v_cell.
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);uid:=x.get_string('uid');
   if ct.CURRENT_CELL is null or ct.CURRENT_CELL!=x.get_string('cell') then raise_application_error(-20887,'CASE_CARRIER_LOCATION_CONFLICT');end if;
   if x.get_string('cell')!=target_cell then
    base:=x.get_string('base');
    declare
 v_json_sql_2_1 varchar2(32767):=x.get_string('article');
begin
select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_json_sql_2_1 and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
end;
    line_no:=line_no+1;
    RRL_STOCK_TRANSFER_CORE.move(uid,uid,x.get_string('cell'),target_cell,RRL_STOCK_MATH.quantity(x.get_string('quantity')),base,ver,ware,p_actor,line_no,null,null,null,null,null,'CASE_TRANSIT');
   end if;
  end loop;
  chunks:=v.get_array('chunks');
  for i in 0..chunks.get_size-1 loop
   x:=treat(chunks.get(i) as json_object_t);uid:=x.get_string('source_uid');target:=x.get_string('target_uid');
   qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));base:=x.get_string('base');sid:=x.get_number('reservation');new_sid:=x.get_number('new_reservation');
   select REMAIN,STOCK_VERSION into physical,stockver from RRL_REMAINS where UID_POLETA=uid and CELL=v_cell;
   if stockver!=x.get_number('stock_version') or RRL_STOCK_PLAN_HELPER.decimal_text(physical)!=x.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: case source stock');end if;
   select BASE_QTY into owned from RRL_STOCK_RESERVATION where RESERVATION_ID=sid and UID_PALLET=uid and CELL=v_cell
    and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=l.PICK_WAVE_ID and SOURCE_LINE_ID=l.PICK_TASK_ID
    and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
   if owned<qty then raise_application_error(-20869,'CASE_OWN_HARD_INSUFFICIENT');end if;
   select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if ver is null or ver!=x.get_number('policy') then raise_application_error(-20890,'CLOSURE_CHANGED: case UOM policy');end if;
   selected:=json_array_t();
   for selected_unit in(select u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u
    join json_table(unit_wire,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_UID=uid and u.CURRENT_CELL=v_cell and u.HARD_RESERVATION_ID=sid and u.STOCK_STATUS!='ISSUED'
    order by u.PHYSICAL_UNIT_KEY) loop
    selected.append(selected_unit.PHYSICAL_UNIT_KEY);matched:=matched+1;
   end loop;
   select count(*) into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
   if n>0 and selected.get_size=0 then raise_application_error(-20884,'CASE_MARKED_UNIT_SCANS_REQUIRED');end if;
   select * into p from RRL_PALLETS where UID_PALLET=uid;
   if p.ARTICUL!=article then raise_application_error(-20887,'CASE_LOT_ARTICLE_CONFLICT');end if;
   p.STOCK_ORIGIN_UID:=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET);p.CREATED_BY_STOCK_OP:=op;p.UID_PALLET:=target;p.SSCC:=null;p.PRINTED:=0;
   if p.WEIGHT_BRUTTO is not null or p.WEIGHT_TN is not null or p.COUNT_KOR is not null then
    if p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20887,'CASE_LOT_BIRTH_QUANTITY_REQUIRED');end if;
    p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*qty/p.UNIT_COUNT;
    p.WEIGHT_TN:=p.WEIGHT_TN*qty/p.UNIT_COUNT;p.COUNT_KOR:=p.COUNT_KOR*qty/p.UNIT_COUNT;
   end if;
   p.UNIT_COUNT:=qty;insert into RRL_PALLETS values p;
   line_no:=line_no+1;
   RRL_STOCK_TRANSFER_CORE.move(uid,target,v_cell,target_cell,qty,base,ver,ware,p_actor,line_no,sid,
    case when selected.get_size>0 then selected.to_clob else null end,new_sid,null,null,'CASE_TRANSIT');
   insert into RRL_CASE_CARRIER_LOT(LOT_UID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,CREATED_OPERATION,CREATED_BY)
    values(target,task_id,line_id,op,p_actor);
   factx:=json_object_t();factx.put('uid',target);factx.put('source_uid',uid);factx.put('quantity',x.get_string('quantity'));factx.put('unit',base);facts.append(factx);
  end loop;
  if matched!=keys.get_size then raise_application_error(-20884,'CASE_SELECTED_UNIT_NOT_OWNED');end if;
  newstatus:=case when fact=l.PLANNED_QTY then 'PICKED' else 'PARTIAL' end;offline:=m.get_string('offline_event_id');
  update RRL_CASE_PICK_LINE set PICKED_QTY=fact,STATUS=newstatus,LAST_OFFLINE_EVENT_ID=offline,
   STARTED_AT=nvl(STARTED_AT,systimestamp),DONE_AT=case when newstatus='PICKED' then systimestamp else DONE_AT end,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_LINE_ID=line_id;
  update RRL_PICK_TASK set FACT_QTY=fact,STATUS=case when newstatus='PICKED' then 'DONE' else 'IN_PROGRESS' end,
   DONE_AT=case when newstatus='PICKED' then sysdate else DONE_AT end,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_TASK_ID=l.PICK_TASK_ID;
  update RRL_PICK_WAVE_TASK set FACT_QTY=fact,STATUS=case when newstatus='PICKED' then 'DONE' else 'IN_PROGRESS' end,
   DONE_AT=case when newstatus='PICKED' then sysdate else DONE_AT end,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_TASK_ID=l.PICK_WAVE_TASK_ID;
  update RRL_CASE_PICK_TASK t set CURRENT_CELL=target_cell,CONTENT_VERSION=CONTENT_VERSION+1,
   (TOTAL_LINES,PICKED_LINES,PLANNED_QTY,PICKED_QTY)=(select count(*),nvl(sum(case when STATUS in('PICKED','SHORT_PICKED','CANCELLED') then 1 else 0 end),0),nvl(sum(PLANNED_QTY),0),nvl(sum(PICKED_QTY),0) from RRL_CASE_PICK_LINE z where z.CASE_PICK_TASK_ID=task_id),
   UPDATED_AT=systimestamp,UPDATED_BY=p_actor where t.CASE_PICK_TASK_ID=task_id;
  select RRL_CASE_PICK_EVENT_SQ.nextval into eventid from dual;
  insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,EVENT_TYPE,OFFLINE_EVENT_ID,PAYLOAD_JSON,CREATED_BY)
   values(eventid,task_id,line_id,'LINE_CONFIRMED',offline,p_request,p_actor);
  v:=json_object_t();v.put('operation_id',op);v.put('case_pick_task_id',task_id);v.put('case_pick_line_id',line_id);v.put('status',newstatus);
  v.put('fact_qty',RRL_STOCK_PLAN_HELPER.decimal_text(fact));v.put('carrier_identifier',ct.SSCC);v.put('cell',target_cell);v.put('picked_from_cell',v_cell);v.put('lots',facts);p_result:=v.to_clob;
 end;
end;
/

create or replace package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
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
  v_result json_object_t:=json_object_t();v_resource number;v_session number;v_equipment number;v_sync_id number;v_sync_key varchar2(400);v_session_actor varchar2(100);v_input_uom varchar2(20);v_source_p number;v_uom_signature varchar2(64);v_sap_header number;v_sap_cell varchar2(60);v_sap_ware number;v_document_confirmation number:=0;
 begin
  v_doc.on_error(1);v_source:=v_doc.get_object('source');v_meta:=v_doc.get_object('metadata');v_meta.on_error(1);
  if v_meta.has('document_confirmation') then v_document_confirmation:=nvl(v_meta.get_number('document_confirmation'),0);end if;
  v_op:=v_doc.get_string('operation_id');v_task_id:=v_source.get_number('task_id');
  
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)));
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
  v_domain:=json_object_t.parse(v_plan).get_object('domain');
  -- Existing assignment/start commands lock the source document before the task.
  -- Read identity without a row lock, validate the planned signature, then use the same order.
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id;
  if v_document_confirmation=1 then
   if v_task.TASK_SOURCE!='MES_RAW_SUPPLY' or RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_confirm')!=1 then raise_application_error(-20882,'MES_DOCUMENT_CONFIRM_FORBIDDEN');end if;
  elsif RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'TASK_COMPLETE_FORBIDDEN');end if;
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string('task_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: task source');end if;
  if v_task.TASK_SOURCE='WAVE' then
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update;
  elsif v_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update;
  elsif v_task.TASK_SOURCE='SAP_RECEIPT' then
   declare
 v_json_sql_1_1 varchar2(32767):=v_domain.get_string('sap_order_id');
begin
select NAKLAD_ID,RECEIVE_CELL,WARE_ID into v_sap_header,v_sap_cell,v_sap_ware from RRL_SAP_SUPPLY_ORDER where ORDER_ID=v_json_sql_1_1 for update;
end;
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
  if v_document_confirmation!=1 and (upper(trim(v_meta.get_string('scanned_pallet'))) is null or
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

create or replace package RRL_PICKING_API as
  function create_plan(
    p_customer_order_id number,
    p_plan_strategy     varchar2 default 'FEFO',
    p_created_by        varchar2 default null
  ) return number;

  procedure cancel_plan(
    p_pick_plan_id number,
    p_updated_by   varchar2 default null
  );
end RRL_PICKING_API;
/

create or replace package body RRL_PICKING_API as
  function active_reserved_qty(
    p_pallet_uid varchar2,
    p_articul    varchar2
  ) return number is
    v_qty number;
  begin
    select nvl(sum(RESERVED_QTY), 0)
      into v_qty
      from RRL_PICK_RESERVATION
     where RESERVATION_STATUS = 'ACTIVE'
       and (RESERVATION_LEVEL='SOFT' or exists(select 1 from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE!='ACTIVE'))
       and PALLET_UID = p_pallet_uid
       and upper(ARTICUL) = upper(p_articul);
    return v_qty;
  end active_reserved_qty;

  procedure log_decision(
    p_pick_plan_id      number,
    p_pick_plan_line_id number,
    p_decision_type     varchar2,
    p_message_text      varchar2,
    p_payload_json      clob default null,
    p_created_by        varchar2 default null
  ) is
  begin
    insert into RRL_PICK_DECISION_LOG (
      PICK_DECISION_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID,
      DECISION_TYPE, MESSAGE_TEXT, PAYLOAD_JSON, CREATED_AT, CREATED_BY
    ) values (
      RRL_PICK_DECISION_LOG_SQ.nextval, p_pick_plan_id, p_pick_plan_line_id,
      substr(p_decision_type, 1, 50), substr(p_message_text, 1, 1000),
      p_payload_json, sysdate, substr(p_created_by, 1, 50)
    );
  end log_decision;

  function create_plan(
    p_customer_order_id number,
    p_plan_strategy     varchar2 default 'FEFO',
    p_created_by        varchar2 default null
  ) return number is
    v_order RRL_CUSTOMER_ORDER%rowtype;
    v_pick_plan_id number;
    v_line_id number;
    v_task_id number;
    v_remaining number;
    v_candidate_available number;
    v_reserved_by_other number;
    v_reserve_qty number;
    v_requested_total number := 0;
    v_planned_total number := 0;
    v_shortage_total number := 0;
    v_line_planned number;
    v_line_shortage number;
    v_task_type varchar2(30);
    v_strategy varchar2(30);
    v_status varchar2(30);
    v_target_cell varchar2(60);
    v_pick_sequence number;
    v_pick_face_id number;
    v_pick_route_cell_id number;
    v_release varchar2(20);v_requested_line_qty number;v_uom varchar2(20);v_version number;v_num number;v_den number;v_scale number;
  begin
    select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;
    v_strategy := upper(nvl(p_plan_strategy, 'FEFO'));
    if v_strategy not in ('FEFO', 'FIFO') then
      raise_application_error(-20980, 'unsupported picking strategy');
    end if;

    select *
      into v_order
      from RRL_CUSTOMER_ORDER
     where CUSTOMER_ORDER_ID = p_customer_order_id;

    select RRL_PICK_PLAN_SQ.nextval into v_pick_plan_id from dual;

    insert into RRL_PICK_PLAN (
      PICK_PLAN_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID, WARE_ID, ROUTE_ID, DOCK_ID,
      STATUS, PLAN_STRATEGY, CREATED_AT, CREATED_BY
    ) values (
      v_pick_plan_id, v_order.CUSTOMER_ORDER_ID, v_order.CUSTOMER_ID, v_order.WARE_ID,
      v_order.ROUTE_ID, v_order.DOCK_ID, 'DRAFT', v_strategy, sysdate, substr(p_created_by, 1, 50)
    );

    for l in (
      select *
        from RRL_CUSTOMER_ORDER_ROW
       where CUSTOMER_ORDER_ID = p_customer_order_id
         and STATUS <> 'CANCELLED'
       order by LINE_NO, CUSTOMER_ORDER_ROW_ID
    ) loop
      select RRL_PICK_PLAN_LINE_SQ.nextval into v_line_id from dual;
      v_requested_line_qty:=nvl(l.ORDER_QTY,0);
      if v_release='ACTIVE' then
       select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=l.UNIT_CODE;
       select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_uom,v_num,v_den,v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=l.UNIT_CODE and POLICY_VERSION=v_version;
       v_requested_line_qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(l.ORDER_QTY),v_num,v_den,v_scale);
      end if;
      v_remaining := v_requested_line_qty;
      v_line_planned := 0;
      v_reserved_by_other := 0;
      v_requested_total := v_requested_total + v_requested_line_qty;

      insert into RRL_PICK_PLAN_LINE (
        PICK_PLAN_LINE_ID, PICK_PLAN_ID, CUSTOMER_ORDER_ROW_ID, ARTICUL,
        PRODUCT_NAME, REQUESTED_QTY, STATUS, CREATED_AT, CREATED_BY
      ) values (
        v_line_id, v_pick_plan_id, l.CUSTOMER_ORDER_ROW_ID, upper(substr(l.ARTICUL, 1, 40)),
        l.PRODUCT_NAME, v_requested_line_qty, 'OPEN', sysdate, substr(p_created_by, 1, 50)
      );

      for c in (
        select r.rowid REMAIN_ROWID,
               r.CELL,
               r.UID_POLETA,
               r.REMAIN,
               p.EXPIRY_DATE,
               p.CREATION_DATE,
               p.PROD_BATCH_ID,
               p.SSCC,
               p.UNIT_COUNT,
               nvl(br.IS_SHIPMENT_ALLOWED, 1) IS_SHIPMENT_ALLOWED
          from RRL_REMAINS r
          join RRL_PALLETS p
            on p.UID_PALLET = r.UID_POLETA
          join RRL_CELLS cc on cc.CELL=r.CELL
          left join RRL_PROD_BATCH_READY_V br
            on br.PROD_BATCH_ID = p.PROD_BATCH_ID
         where r.REMAIN > 0
           and (v_release!='ACTIVE' or (cc.WARE_ID=v_order.WARE_ID and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0 and r.BASE_UOM=v_uom))
           and upper(p.ARTICUL) = upper(l.ARTICUL)
         order by case when v_strategy = 'FEFO' then p.EXPIRY_DATE end nulls last,
                  case when v_strategy = 'FIFO' then p.CREATION_DATE end nulls last,
                  r.TIME_OF_LAST_UPDATE nulls last,
                  r.UID_POLETA
      ) loop
        exit when v_remaining <= 0;

        declare
          v_locked_remain number;
        begin
          if v_release='ACTIVE' then
           select REMAIN-HARD_RESERVED_BASE into v_locked_remain from RRL_REMAINS where rowid=c.REMAIN_ROWID;
          else
          select REMAIN
            into v_locked_remain
            from RRL_REMAINS
           where rowid = c.REMAIN_ROWID
           for update;
          end if;

          if c.IS_SHIPMENT_ALLOWED = 0 then
            log_decision(
              v_pick_plan_id,
              v_line_id,
              'SKIP_NOT_READY',
              'Pallet skipped because batch is not allowed for shipment',
              '{"pallet":"' || replace(c.UID_POLETA, '"', '\"') || '"}',
              p_created_by
            );
          else
            v_candidate_available := greatest(nvl(v_locked_remain, 0) - active_reserved_qty(c.UID_POLETA, l.ARTICUL), 0);
            v_reserved_by_other := v_reserved_by_other + (nvl(v_locked_remain, 0) - v_candidate_available);

            if v_candidate_available > 0 then
              v_reserve_qty := least(v_remaining, v_candidate_available);
              if v_reserve_qty >= v_candidate_available then
                v_task_type := 'FULL_PALLET';
              else
                v_task_type := 'CASE_PICK';
              end if;

              v_target_cell := null;
              v_pick_sequence := null;
              v_pick_face_id := null;
              v_pick_route_cell_id := null;

              if v_task_type = 'CASE_PICK' then
                RRL_PICK_TOPOLOGY_API.resolve_pick_face(
                  p_ware_id => v_order.WARE_ID,
                  p_articul => l.ARTICUL,
                  p_target_cell => v_target_cell,
                  p_pick_sequence => v_pick_sequence,
                  p_pick_face_id => v_pick_face_id,
                  p_pick_route_cell_id => v_pick_route_cell_id
                );

                if v_target_cell is not null then
                  log_decision(
                    v_pick_plan_id,
                    v_line_id,
                    'PICK_FACE_SELECTED',
                    'Case-pick task assigned to configured pick face',
                    '{"articul":"' || replace(l.ARTICUL, '"', '\"') || '","targetCell":"' || replace(v_target_cell, '"', '\"') || '"}',
                    p_created_by
                  );
                else
                  log_decision(
                    v_pick_plan_id,
                    v_line_id,
                    'NO_PICK_FACE',
                    'No active pick face found for case-pick task',
                    '{"articul":"' || replace(l.ARTICUL, '"', '\"') || '"}',
                    p_created_by
                  );
                end if;
              end if;

              select RRL_PICK_TASK_SQ.nextval into v_task_id from dual;
              insert into RRL_PICK_TASK (
                PICK_TASK_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID,
                TASK_TYPE, STATUS, ARTICUL, PALLET_UID, SSCC, PROD_BATCH_ID,
                SOURCE_CELL_CODE, TARGET_CELL_CODE, QTY, PICK_SEQUENCE,
                PICK_FACE_ID, PICK_ROUTE_CELL_ID, CREATED_AT, CREATED_BY
              ) values (
                v_task_id, v_pick_plan_id, v_line_id, p_customer_order_id, v_order.CUSTOMER_ID,
                v_task_type, 'NEW', upper(substr(l.ARTICUL, 1, 40)), c.UID_POLETA,
                c.SSCC, c.PROD_BATCH_ID, c.CELL, v_target_cell, v_reserve_qty,
                v_pick_sequence, v_pick_face_id, v_pick_route_cell_id, sysdate, substr(p_created_by, 1, 50)
              );

              insert into RRL_PICK_RESERVATION (
                PICK_RESERVATION_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID, PICK_TASK_ID,
                CUSTOMER_ORDER_ID, CUSTOMER_ID, RESERVATION_LEVEL, RESERVATION_STATUS,
                RESERVATION_SCOPE, PALLET_UID, SSCC, ARTICUL, PROD_BATCH_ID,
                SOURCE_CELL_CODE, RESERVED_QTY, CREATED_AT, CREATED_BY
              ) values (
                RRL_PICK_RESERVATION_SQ.nextval, v_pick_plan_id, v_line_id, v_task_id,
                p_customer_order_id, v_order.CUSTOMER_ID, 'SOFT', 'ACTIVE',
                case when v_task_type = 'FULL_PALLET' then 'PALLET' else 'CASE' end,
                c.UID_POLETA, c.SSCC, upper(substr(l.ARTICUL, 1, 40)), c.PROD_BATCH_ID,
                c.CELL, v_reserve_qty, sysdate, substr(p_created_by, 1, 50)
              );

              v_line_planned := v_line_planned + v_reserve_qty;
              v_remaining := v_remaining - v_reserve_qty;
            end if;
          end if;
        exception
          when no_data_found then
            null;
        end;
      end loop;

      v_line_shortage := greatest(v_requested_line_qty - v_line_planned, 0);
      v_planned_total := v_planned_total + v_line_planned;
      v_shortage_total := v_shortage_total + v_line_shortage;

      update RRL_PICK_PLAN_LINE
         set PLANNED_QTY = v_line_planned,
             FULL_PALLET_QTY = nvl((
               select sum(QTY)
                 from RRL_PICK_TASK
                where PICK_PLAN_LINE_ID = v_line_id
                  and TASK_TYPE = 'FULL_PALLET'
             ), 0),
             CASE_PICK_QTY = nvl((
               select sum(QTY)
                 from RRL_PICK_TASK
                where PICK_PLAN_LINE_ID = v_line_id
                  and TASK_TYPE = 'CASE_PICK'
             ), 0),
             SHORTAGE_QTY = v_line_shortage,
             STATUS = case
               when v_line_shortage = 0 then 'PLANNED_FULL'
               when v_line_planned > 0 then 'PLANNED_PARTIAL'
               else 'NO_STOCK'
             end,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_created_by, 1, 50)
       where PICK_PLAN_LINE_ID = v_line_id;

      if v_line_shortage > 0 then
        insert into RRL_PICK_SHORTAGE (
          PICK_SHORTAGE_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID,
          CUSTOMER_ORDER_ID, CUSTOMER_ORDER_ROW_ID, CUSTOMER_ID, ARTICUL,
          REQUESTED_QTY, AVAILABLE_QTY, RESERVED_BY_OTHER_QTY, PLANNED_QTY,
          SHORTAGE_QTY, REASON_CODE, REASON_TEXT, CREATED_AT, CREATED_BY
        ) values (
          RRL_PICK_SHORTAGE_SQ.nextval, v_pick_plan_id, v_line_id,
          p_customer_order_id, l.CUSTOMER_ORDER_ROW_ID, v_order.CUSTOMER_ID,
          upper(substr(l.ARTICUL, 1, 40)), v_requested_line_qty,
          v_line_planned, v_reserved_by_other, v_line_planned,
          v_line_shortage, 'NO_FREE_STOCK',
          'Free stock is not enough after active reservations',
          sysdate, substr(p_created_by, 1, 50)
        );
      end if;
    end loop;

    if v_requested_total = 0 then
      v_status := 'NO_STOCK';
    elsif v_planned_total = 0 then
      v_status := 'NO_STOCK';
    elsif v_shortage_total > 0 then
      v_status := 'PLANNED_PARTIAL';
    else
      v_status := 'PLANNED_FULL';
    end if;

    update RRL_PICK_PLAN
       set STATUS = v_status,
           TOTAL_ORDER_QTY = v_requested_total,
           TOTAL_PLANNED_QTY = v_planned_total,
           TOTAL_SHORTAGE_QTY = v_shortage_total,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_created_by, 1, 50)
     where PICK_PLAN_ID = v_pick_plan_id;

    log_decision(
      v_pick_plan_id,
      null,
      'PLAN_CREATED',
      'Picking plan created with soft reservations',
      '{"requested":' || to_char(v_requested_total) || ',"planned":' || to_char(v_planned_total) || ',"shortage":' || to_char(v_shortage_total) || '}',
      p_created_by
    );

    return v_pick_plan_id;
  end create_plan;

  procedure cancel_plan(
    p_pick_plan_id number,
    p_updated_by   varchar2 default null
  ) is
  begin
    declare st varchar2(20);j json_object_t:=json_object_t();src json_object_t:=json_object_t();m json_object_t:=json_object_t();result clob;kind varchar2(80);request clob;doc number;
    begin
      select STATE into st from RRL_STOCK_RELEASE where RELEASE_ID=1;
      if st='ACTIVE' then
        if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then
          select COMMAND_TYPE,CANONICAL_REQUEST into kind,request from RRL_STOCK_OPERATION where OPERATION_ID=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
          doc:=json_object_t.parse(request).get_object('source').get_number('document_id');
          if kind!='PICK_PLAN_CANCEL' or doc!=p_pick_plan_id then raise_application_error(-20863,'PLAN_CANCEL_CONTEXT_CONFLICT');end if;
        else
          j.put('contract_version',2);j.put('operation_id','PLAN.CANCEL:'||to_char(p_pick_plan_id,'TM9'));j.put('command_type','PICK_PLAN_CANCEL');j.put('actor',p_updated_by);
          src.put('document_type','PICK_PLAN');src.put('document_id',p_pick_plan_id);j.put('source',src);j.put('lines',json_array_t());j.put('units',json_array_t());
          m.put('reason','Picking plan cancelled');m.put('only_cancelled_replenishment',0);m.put_null('reservation_kind');j.put('metadata',m);
          RRL_STOCK_NATIVE_API.post(j.to_clob,p_updated_by,result);return;
        end if;
      end if;
    end;

    update RRL_PICK_RESERVATION
       set RESERVATION_STATUS = 'RELEASED',
           RELEASED_AT = sysdate,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_PLAN_ID = p_pick_plan_id
       and RESERVATION_STATUS = 'ACTIVE';

    update RRL_PICK_TASK
       set STATUS = 'CANCELLED',
           ERROR_TEXT = 'Plan cancelled before execution',
           UPDATED_AT = sysdate
     where PICK_PLAN_ID = p_pick_plan_id
       and STATUS in ('NEW', 'ASSIGNED');

    update RRL_PICK_PLAN
       set STATUS = 'CANCELLED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_PLAN_ID = p_pick_plan_id
       and STATUS not in ('DONE');

    log_decision(
      p_pick_plan_id,
      null,
      'PLAN_CANCELLED',
      'Picking plan cancelled and active reservations released',
      null,
      p_updated_by
    );
  end cancel_plan;
end RRL_PICKING_API;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer

 accessible by(package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,

 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as

 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob;

 procedure admit_captured(p_uid varchar2,p_cell varchar2);

 procedure assert_composition(p_uid varchar2,p_cell varchar2);

 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);

 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);

 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);

end;
/

create or replace package body RRL_STOCK_UNIT_CORE as

 procedure require_context is

 begin

  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or

   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or

   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then

   raise_application_error(-20863,'UNIT_WRITE_FORBIDDEN');end if;

 end;

 procedure own_unit(p_key varchar2) is

 begin

  if p_key is null then raise_application_error(-20884,'UNIT_BINDING_REQUIRED');end if;

  begin RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',p_key));

  exception when others then if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: units');else raise;end if;end;

 end;

 procedure assert_composition(p_uid varchar2,p_cell varchar2) is

  v_p number;v_base varchar2(20);v_total number;v_count number;v_bad number;v_article varchar2(160);v_marked number;v_scale number;

 begin

  select REMAIN,BASE_UOM into v_p,v_base from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;

  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;

  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article),0),

   nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=v_article),0),

   case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article) then 1 else 0 end) into v_marked from dual;

  select count(*),nvl(sum(BASE_QTY),0),nvl(sum(case when PHYSICAL_UNIT_KEY is null or STOCK_STATUS is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=v_base then 1 else 0 end),0)

   into v_count,v_total,v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED');

  select max(BASE_SCALE) into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and BASE_UOM=v_base;

  if v_scale is null then raise_application_error(-20868,'COMPOSITION_BASE_POLICY_REQUIRED');end if;

  select count(*) into v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED')

   and (STOCK_STATUS is null or BASE_QTY is null or BASE_QTY<=0 or abs(BASE_QTY)>=power(10,18) or trunc(BASE_QTY,v_scale)!=BASE_QTY or BASE_UOM is null or BASE_UOM!=v_base or PHYSICAL_UNIT_KEY is null);

  if v_bad>0 or (v_count>0 and v_total!=v_p) or (v_marked=1 and v_p>0 and v_count=0) then

   raise_application_error(-20884,'PHYSICAL_COMPOSITION_CONFLICT');end if;

 end;

 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob is

  a json_array_t:=json_array_t();v_n number;v_qty number:=0;

 begin

  require_context;assert_composition(p_uid,p_cell);

  select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';

  if v_n=0 then return null;end if;

  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='AVAILABLE' and HARD_RESERVATION_ID is null order by PHYSICAL_UNIT_KEY) loop

   exit when v_qty=p_qty;

   own_unit(u.PHYSICAL_UNIT_KEY);

   if v_qty+u.BASE_QTY>p_qty then raise_application_error(-20884,'PHYSICAL_UNIT_ALLOCATION_REQUIRES_SELECTION');end if;

   a.append(u.PHYSICAL_UNIT_KEY);v_qty:=v_qty+u.BASE_QTY;

   if a.get_size>10000 then raise_application_error(-20884,'UNIT_SELECTION_BOUND');end if;

  end loop;

  if v_qty!=p_qty then raise_application_error(-20884,'ADMITTED_FREE_UNITS_INSUFFICIENT');end if;

  return a.to_clob;

 end;

 procedure admit_captured(p_uid varchar2,p_cell varchar2) is

 begin

  require_context;assert_composition(p_uid,p_cell);

  for u in(select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED') loop own_unit(u.PHYSICAL_UNIT_KEY);end loop;

  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);

  update RRL_WMS_RECEIPT_UNIT set STOCK_STATUS='AVAILABLE',UNIT_VERSION=UNIT_VERSION+1

   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED';

  RRL_STOCK_CTX_API.end_effect;

 end;

 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob) is v_total number;v_count number;v_qty number;v_expected number;v_distinct number;

 begin

  require_context;assert_composition(p_uid,p_cell);

  select count(*) into v_total from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';

  if v_total=0 then return;end if;

  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u

   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'

    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));

  if v_qty!=p_qty then raise_application_error(-20884,'ISSUE_UNIT_QUANTITY_CONFLICT');end if;

  if p_units is not null then

   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));

   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;

  end if;

  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u

   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'

    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop

   own_unit(r.PHYSICAL_UNIT_KEY);

   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_RESERVED_BY_OTHER_OWNER');end if;

   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;

  end loop;

  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);

  update RRL_WMS_RECEIPT_UNIT u set STOCK_STATUS='ISSUED',UNIT_VERSION=UNIT_VERSION+1

   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'

    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));

  RRL_STOCK_CTX_API.end_effect;

 end;

 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob) is

  v_count number;v_total number;v_chosen number;v_qty number;v_expected number;

 begin

  require_context;assert_composition(p_uid,p_cell);

  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));

  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_total from RRL_WMS_RECEIPT_UNIT

   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';

  if v_count=0 then return;end if;

  select count(*),nvl(sum(BASE_QTY),0) into v_chosen,v_qty from RRL_WMS_RECEIPT_UNIT u

   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'

    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));

  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;

  if p_units is not null then

   select count(*),count(distinct K) into v_expected,v_count from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));

   if v_expected!=v_count or v_expected!=v_chosen then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;

  end if;

  for r in(select PHYSICAL_UNIT_KEY,HARD_RESERVATION_ID,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u

   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'

    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop

   own_unit(r.PHYSICAL_UNIT_KEY);

   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_ALREADY_RESERVED');end if;

   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;

  end loop;

  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);

  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=p_id,UNIT_VERSION=UNIT_VERSION+1

   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'

    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));

  RRL_STOCK_CTX_API.end_effect;

 end;

 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0) is

  v_qty number;v_count number;v_expected number;v_distinct number;v_uid varchar2(200);v_cell varchar2(60);

 begin

  require_context;

  select UID_PALLET,CELL into v_uid,v_cell from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id;

  assert_composition(v_uid,v_cell);

  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));

  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u

   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'

    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));

  if v_count=0 then

   select count(*) into v_expected from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';

   if v_expected>0 then raise_application_error(-20869,'RESERVATION_UNIT_BINDING_REQUIRED');end if;

   return;end if;

  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;

  if p_units is not null then

   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));

   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;

  end if;

  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u

   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'

    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop

   own_unit(r.PHYSICAL_UNIT_KEY);

   if p_issue=1 and r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;

  end loop;

  RRL_STOCK_CTX_API.begin_effect('UNIT',v_uid,v_cell);

  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=null,UNIT_VERSION=UNIT_VERSION+1,

   STOCK_STATUS=case when p_issue=1 then 'ISSUED' else STOCK_STATUS end

   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'

    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));

  RRL_STOCK_CTX_API.end_effect;

 end;

end;
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

    -- Conversion version describes input units; balances always use the

    -- latest identity policy for their canonical base unit.

    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION

     where ARTICUL=v_article and INPUT_UOM=v_base and BASE_UOM=v_base

       and NUMERATOR=1 and DENOMINATOR=1;

    if v_version is null then raise_application_error(-20868,'BASE_IDENTITY_POLICY_REQUIRED');end if;

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

drop package RRL_STOCK_ELIGIBILITY;
/
-- Keep additive SOURCE_PICK_MODE column/data; do not silently erase configured rules.

@@../2026-10-08_stock_posting_core/014b_recompile.sql
