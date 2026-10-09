declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_CTX_API authid definer
 accessible by(package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_BALANCE_CORE,package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_UNIT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_CONFIG_API,package RRL_STOCK_POSTING_API,package RRL_STOCK_OPERATION_CORE) as
 procedure open_operation(p_operation varchar2,p_mode varchar2 default 'EXPLICIT');
 procedure open_configuration(p_actor varchar2,p_permission varchar2);
 procedure begin_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null);
 procedure begin_staging(p_uid varchar2,p_cell varchar2);
 procedure end_effect;
 procedure clear_operation;
end;
/

create or replace package RRL_STOCK_LOCATION_CORE authid definer
 accessible by(package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number);
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number);
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2);
end;
/

create or replace package RRL_STOCK_MES_SUPPLY_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_CTX_API as
 procedure open_operation(p_operation varchar2,p_mode varchar2 default 'EXPLICIT') is v_state varchar2(20);
 begin
  select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_state!='ACTIVE' then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE'); end if;
  if p_mode not in('EXPLICIT','COMPAT') then raise_application_error(-20861,'STOCK_CONTEXT_MODE_INVALID'); end if;
  RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',p_operation));
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then raise_application_error(-20862,'POSTING_ALREADY_ENTERED'); end if;
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','OPERATION_ID',p_operation);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','TX_ID',dbms_transaction.local_transaction_id(false));
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','MODE',p_mode);
 end;
 procedure begin_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null) is v_tx varchar2(100);
 begin
  v_tx:=dbms_transaction.local_transaction_id(false);
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or v_tx is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=v_tx
   or p_kind is null or p_kind not in('STOCK','JOURNAL','RESERVATION','UNIT') then raise_application_error(-20863,'EFFECT_CONTEXT_FORBIDDEN');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','EFFECT') is not null then raise_application_error(-20862,'NESTED_EFFECT_FORBIDDEN');end if;
  if p_uid is not null then RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));end if;
  if p_kind in('STOCK','JOURNAL','UNIT') and p_uid is null then raise_application_error(-20863,'EFFECT_UID_REQUIRED');end if;
  if p_kind='RESERVATION' then
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(p_row_id)));
  end if;
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT',p_kind);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_UID',p_uid);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_CELL',p_cell);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_ROW_ID',RRL_STOCK_PLAN_HELPER.decimal_text(p_row_id));
 end;
 procedure begin_staging(p_uid varchar2,p_cell varchar2) is
 begin
  begin_effect('UNIT',p_uid,p_cell);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT','RECEIPT_CAPTURE');
 end;
 procedure end_effect is
 begin
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT',null);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_UID',null);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_CELL',null);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_ROW_ID',null);
 end;
 procedure open_configuration(p_actor varchar2,p_permission varchar2) is
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then raise_application_error(-20862,'POSTING_ALREADY_ENTERED');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','TX_ID',dbms_transaction.local_transaction_id(false));
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','MODE','CONFIG');
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','ACTOR',p_actor);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION',p_permission);
 end;
 procedure clear_operation is
 begin
  dbms_session.clear_context('RRL_STOCK_WRITE_CTX',null);
 end;
end;
/

create or replace package body RRL_STOCK_LOCATION_CORE as
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number) is v_ware number;v_block number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID,nvl(BLOCKED_FOR_ACCEPT,0) into v_ware,v_block from RRL_CELLS where CELL=p_cell;
  if v_ware is null or p_expected_warehouse is null or v_ware!=p_expected_warehouse or v_block!=0 then raise_application_error(-20879,'RECEIVING_LOCATION_UNAVAILABLE');end if;
 end;
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number) is v_ware number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_cell;
  if v_ware is null or p_expected_warehouse is null or v_ware!=p_expected_warehouse then raise_application_error(-20877,'QUARANTINE_WAREHOUSE_CONFLICT');end if;
 end;
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2) is
  v_ware number;v_remain number;v_replenish number;v_accept number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID,nvl(BLOCKED_FOR_REMAINS,0),nvl(BLOCKED_FOR_POPOLNENIE,0),nvl(BLOCKED_FOR_ACCEPT,0)
   into v_ware,v_remain,v_replenish,v_accept from RRL_CELLS where CELL=p_cell;
  if p_expected_warehouse is null or v_ware is null or v_ware!=p_expected_warehouse then
   raise_application_error(-20877,'WAREHOUSE_LOCATION_CONFLICT');
  end if;
  if p_role not in('SOURCE','TARGET','RECEIVE') or p_role is null then raise_application_error(-20878,'LOCATION_ROLE_INVALID'); end if;
  if v_remain!=0 or v_replenish!=0 or(p_role in('TARGET','RECEIVE') and v_accept!=0) then
   raise_application_error(-20879,'LOCATION_BLOCKED: quarantine/unavailable cell excluded');
  end if;
 end;
end;
/

create or replace package body RRL_STOCK_MES_SUPPLY_CMD as
 function nonnegative(p_text varchar2) return number is
 begin if p_text='0' then return 0;end if;return RRL_STOCK_MATH.quantity(p_text);end;

 function convert_qty(p_article varchar2,p_unit varchar2,p_qty number,p_base out varchar2) return number is
  n number;dn number;sc number;ver number;
 begin
  if p_qty is null or p_qty<0 then raise_application_error(-20869,'MES_QUANTITY_INVALID');end if;
  select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=p_unit;
  if ver is null then raise_application_error(-20868,'MES_UOM_REQUIRED');end if;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into p_base,n,dn,sc from RRL_STOCK_UOM_CONVERSION
   where ARTICUL=p_article and INPUT_UOM=p_unit and POLICY_VERSION=ver;
  if p_qty=0 then return 0;end if;
  return RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(p_qty),n,dn,sc);
 end;
 function lines_json(p_order number) return clob is a json_array_t:=json_array_t();x json_object_t;
  req number;iss number;b varchar2(20);mb varchar2(20);n number;
 begin
  for l in(select * from RRL_PROD_ORDER_BOM_LINE where PRODUCTION_ORDER_ID=p_order and COMPONENT_ARTICUL is not null order by ORDER_LINE_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'MES_BOM_BATCH_BOUND');end if;
   req:=convert_qty(l.COMPONENT_ARTICUL,l.UNIT_CODE,l.PLANNED_QTY,b);iss:=0;
   for m in(select BOM_LINE_ID,QUANTITY,UNIT_CODE from RRL_MES_MOVEMENT where PRODUCTION_ORDER_ID=p_order and MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION'
    and STATUS<>'CANCELLED' and RAW_ARTICUL=l.COMPONENT_ARTICUL and (BOM_LINE_ID=l.BOM_LINE_ID or BOM_LINE_ID is null)) loop
    if m.BOM_LINE_ID is null then
     select count(*) into n from RRL_PROD_ORDER_BOM_LINE where PRODUCTION_ORDER_ID=p_order and COMPONENT_ARTICUL=l.COMPONENT_ARTICUL;
     if n!=1 then raise_application_error(-20869,'MES_ISSUED_BOM_LINE_AMBIGUOUS');end if;
    end if;
    iss:=iss+convert_qty(l.COMPONENT_ARTICUL,m.UNIT_CODE,m.QUANTITY,mb);
    if mb!=b then raise_application_error(-20868,'MES_BASE_UOM_CONFLICT');end if;
   end loop;
   x:=json_object_t();x.put('line',l.ORDER_LINE_ID);x.put('bom',l.BOM_ID);x.put('bom_line',l.BOM_LINE_ID);x.put('article',l.COMPONENT_ARTICUL);
   x.put('required',RRL_STOCK_PLAN_HELPER.decimal_text(req));x.put('issued',RRL_STOCK_PLAN_HELPER.decimal_text(iss));x.put('base',b);a.append(x);
  end loop;return a.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t:=json_object_t();x json_object_t;y json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;b json_array_t:=json_array_t();oldsr json_array_t:=json_array_t();
  doc number;task number;sr number;wid number;id number;qty number;remainq number;freeq number;total number;ware number;target varchar2(60);
  base varchar2(20);ver number;pending number;raw clob;
  type qty_map is table of number index by varchar2(2000);used qty_map;k varchar2(2000);
 begin
  doc:=d.get_object('source').get_number('production_order_id');target:=d.get_object('metadata').get_string('to_cell');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRODUCTION_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(doc));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  select count(*) into pending from RRL_MES_RAW_TRANSFER_TASK where PRODUCTION_ORDER_ID=doc and TASK_STATUS in('PLANNED','IN_PROGRESS');
  v.put('pending',pending);v.put('document',doc);
  if pending=0 then
   select WARE_ID into ware from RRL_CELLS where CELL=target;
   if d.get_object('metadata').get_number('to_ware_id') is not null and d.get_object('metadata').get_number('to_ware_id')!=ware then raise_application_error(-20869,'MES_TARGET_WARE_CONFLICT');end if;
   RRL_STOCK_PLAN_HELPER.fence(f,'CELL',target);v.put('target',target);v.put('warehouse',ware);
   raw:=lines_json(doc);a:=json_array_t.parse(raw);v.put('signature',rawtohex(sys.dbms_crypto.hash(raw,sys.dbms_crypto.hash_sh256)));
   for s in(select * from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PRODUCTION_ORDER' and SOURCE_DOC_ID=doc and RESERVATION_KIND='SOFT' and STATUS in('ACTIVE','ALLOCATED')) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(s.RESERVATION_ID));x:=json_object_t();x.put('id',s.RESERVATION_ID);x.put('version',s.RESERVATION_VERSION);oldsr.append(x);
   end loop;
   for i in 0..a.get_size-1 loop
    x:=treat(a.get(i) as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PROD_ORDER_BOM_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('line')));
    RRL_STOCK_PLAN_HELPER.fence(f,'SKU',x.get_string('article'));
    select RRL_MES_RAW_DEMAND_SQ.nextval into id from dual;x.put('demand',id);
    remainq:=greatest(nonnegative(x.get_string('required'))-nonnegative(x.get_string('issued')),0);
    x.put('open',RRL_STOCK_PLAN_HELPER.decimal_text(remainq));x.put_null('soft');
    if remainq>0 then select RRL_STOCK_RESERVATION_SQ.nextval into sr from dual;x.put('soft',sr);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr));end if;
    for c in(select rr.UID_POLETA,rr.CELL,rr.REMAIN,rr.HARD_RESERVED_BASE,rr.BASE_UOM,cc.WARE_ID
     from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA join RRL_CELLS cc on cc.CELL=rr.CELL join RRL_WARES ww on ww.ID=cc.WARE_ID
     where pp.ARTICUL=x.get_string('article') and ww.FLAG_RAW_MATERIAL=1 and rr.REMAIN>rr.HARD_RESERVED_BASE
      and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0 and rr.CELL!=target
     order by pp.EXPIRY_DATE nulls last,pp.PRODUCED_DATE nulls last,rr.CELL,rr.UID_POLETA) loop
     exit when remainq=0;if b.get_size>=1000 then raise_application_error(-20881,'MES_ALLOCATION_BATCH_BOUND');end if;
     if c.BASE_UOM!=x.get_string('base') then raise_application_error(-20868,'MES_SOURCE_BASE_CONFLICT');end if;
     k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA,c.CELL));if not used.exists(k) then used(k):=0;end if;
     freeq:=c.REMAIN-c.HARD_RESERVED_BASE-used(k);if freeq<=0 then continue;end if;
     qty:=least(freeq,remainq);used(k):=used(k)+qty;remainq:=remainq-qty;
     select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=x.get_string('article') and INPUT_UOM=c.BASE_UOM and BASE_UOM=c.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
     if ver is null then raise_application_error(-20868,'MES_BASE_POLICY_REQUIRED');end if;
     select RRL_STOCK_RESERVATION_SQ.nextval,RRL_MES_RAW_TRANSFER_TASK_SQ.nextval,RRL_WAREHOUSE_TASK_SQ.nextval,RRL_MES_RAW_SUPPLY_CANDIDATE_SQ.nextval into sr,task,wid,id from dual;
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr));
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_MES_RAW_TRANSFER_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(wid));
     RRL_STOCK_PLAN_HELPER.stock_closure(f,r,c.UID_POLETA,x.get_string('article'),c.CELL,null);
     y:=json_object_t();y.put('demand',x.get_number('demand'));y.put('reservation',sr);y.put('task',task);y.put('warehouse_task',wid);y.put('candidate',id);
     y.put('uid',c.UID_POLETA);y.put('cell',c.CELL);y.put('ware',c.WARE_ID);y.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));y.put('physical',RRL_STOCK_PLAN_HELPER.decimal_text(c.REMAIN));
     y.put('hard',RRL_STOCK_PLAN_HELPER.decimal_text(c.HARD_RESERVED_BASE));y.put('uom_version',ver);y.put('line_index',i);b.append(y);
    end loop;
    x.put('shortage',RRL_STOCK_PLAN_HELPER.decimal_text(remainq));
    if remainq>0 then select RRL_MES_RAW_SHORTAGE_SQ.nextval into id from dual;x.put('shortage_id',id);end if;
    a.put(i,x);
   end loop;
   v.put('lines',a);v.put('allocations',b);v.put('old_soft',oldsr);
  end if;
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;y json_object_t;detail json_object_t;result json_object_t:=json_object_t();
  plan clob;a json_array_t;b json_array_t;oldsr json_array_t;doc number;pending number;qty number;req number;iss number;oq number;shortq number;n number;cnt number:=0;
  status varchar2(40);raw clob;unitkeys clob;pal RRL_PALLETS%rowtype;old RRL_STOCK_RESERVATION%rowtype;
 begin
  if RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_create')!=1 then raise_application_error(-20882,'MES_RELEASE_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');v:=json_object_t.parse(plan).get_object('domain');doc:=v.get_number('document');
  select STATUS into status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=doc for update;
  if status is null or status in('COMPLETED','CANCELLED') then raise_application_error(-20886,'MES_ORDER_NOT_OPEN');end if;
  select count(*) into pending from RRL_MES_RAW_TRANSFER_TASK where PRODUCTION_ORDER_ID=doc and TASK_STATUS in('PLANNED','IN_PROGRESS');
  if pending!=v.get_number('pending') then raise_application_error(-20890,'CLOSURE_CHANGED: MES pending tasks');end if;
  if pending>0 then result.put('task_count',pending);result.put('existing',1);p_result:=result.to_clob;return;end if;
  a:=v.get_array('lines');b:=v.get_array('allocations');oldsr:=v.get_array('old_soft');
  for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);select ORDER_LINE_ID into n from RRL_PROD_ORDER_BOM_LINE where ORDER_LINE_ID=x.get_number('line') for update;end loop;
  raw:=lines_json(doc);if rawtohex(sys.dbms_crypto.hash(raw,sys.dbms_crypto.hash_sh256))!=v.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: MES requirements');end if;
  RRL_STOCK_LOCATION_CORE.assert_ordinary(v.get_string('target'),v.get_number('warehouse'),'TARGET');
  for i in 0..oldsr.get_size-1 loop
   x:=treat(oldsr.get(i) as json_object_t);select * into old from RRL_STOCK_RESERVATION where RESERVATION_ID=x.get_number('id') for update;
   if old.RESERVATION_VERSION!=x.get_number('version') or old.RESERVATION_KIND!='SOFT' or old.STATUS not in('ACTIVE','ALLOCATED') then raise_application_error(-20890,'CLOSURE_CHANGED: MES soft demand');end if;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,old.RESERVATION_ID);
   update RRL_STOCK_RESERVATION set STATUS='CANCELLED',RELEASED_AT=systimestamp,RELEASED_BY=p_actor,RELEASE_REASON='MES raw supply recalculation',RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=old.RESERVATION_ID;RRL_STOCK_CTX_API.end_effect;
  end loop;
  delete from RRL_MES_RAW_SUPPLY_CANDIDATE where PRODUCTION_ORDER_ID=doc;delete from RRL_MES_RAW_SHORTAGE where PRODUCTION_ORDER_ID=doc;delete from RRL_MES_RAW_DEMAND where PRODUCTION_ORDER_ID=doc;
  shortq:=0;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);req:=nonnegative(x.get_string('required'));iss:=nonnegative(x.get_string('issued'));oq:=nonnegative(x.get_string('open'));qty:=nonnegative(x.get_string('shortage'));
   if oq>0 then
    RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,x.get_number('soft'));
    insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,PRODUCTION_ORDER_ID,ARTICUL,QTY,UNIT_CODE,STATUS,PRIORITY,CREATED_BY,RESERVATION_VERSION)
     values(x.get_number('soft'),'SOFT','QTY','MES_RAW','PRODUCTION_ORDER',doc,x.get_number('line'),doc,x.get_string('article'),oq,x.get_string('base'),'ACTIVE',100,p_actor,0);RRL_STOCK_CTX_API.end_effect;
   end if;
   insert into RRL_MES_RAW_DEMAND(DEMAND_ID,PRODUCTION_ORDER_ID,ORDER_LINE_ID,BOM_ID,BOM_LINE_ID,RAW_ARTICUL,REQUIRED_QTY,ISSUED_QTY,OPEN_QTY,UNIT_CODE,SOFT_RESERVATION_ID,STATUS,CALCULATED_BY)
    values(x.get_number('demand'),doc,x.get_number('line'),x.get_number('bom'),x.get_number('bom_line'),x.get_string('article'),req,iss,oq,x.get_string('base'),x.get_number('soft'),case when oq>0 then 'OPEN' else 'COVERED' end,p_actor);
   if qty>0 then
    shortq:=shortq+1;
    insert into RRL_MES_RAW_SHORTAGE(SHORTAGE_ID,PRODUCTION_ORDER_ID,DEMAND_ID,RAW_ARTICUL,REQUIRED_QTY,ISSUED_QTY,AVAILABLE_QTY,SHORTAGE_QTY,UNIT_CODE,STATUS)
     values(x.get_number('shortage_id'),doc,x.get_number('demand'),x.get_string('article'),req,iss,oq-qty,qty,x.get_string('base'),'OPEN');
   end if;
  end loop;
  for i in 0..b.get_size-1 loop
   y:=treat(b.get(i) as json_object_t);x:=treat(a.get(y.get_number('line_index')) as json_object_t);qty:=RRL_STOCK_MATH.quantity(y.get_string('quantity'));
   select * into pal from RRL_PALLETS where UID_PALLET=y.get_string('uid');
   if pal.ARTICUL!=x.get_string('article') then raise_application_error(-20890,'CLOSURE_CHANGED: MES source article');end if;
   RRL_STOCK_LOCATION_CORE.assert_ordinary(y.get_string('cell'),y.get_number('ware'),'SOURCE');
   insert into RRL_MES_RAW_SUPPLY_CANDIDATE(CANDIDATE_ID,DEMAND_ID,PRODUCTION_ORDER_ID,RAW_ARTICUL,UID_PALLET,BATCH_ID,RAW_BATCH_ID,SSCC,FROM_WARE_ID,FROM_CELL,PHYSICAL_QTY,HARD_RESERVED_QTY,AVAILABLE_QTY,SUGGESTED_QTY,EXPIRY_DATE,QUALITY_STATUS,SORT_ORDER)
    values(y.get_number('candidate'),x.get_number('demand'),doc,x.get_string('article'),pal.UID_PALLET,to_char(pal.PRIHOD_NAKLAD_ID),pal.PRIHOD_NAKLAD_ID,pal.SSCC,y.get_number('ware'),y.get_string('cell'),RRL_STOCK_MATH.quantity(y.get_string('physical')),nonnegative(y.get_string('hard')),qty,qty,pal.EXPIRY_DATE,pal.QUALITY_STATUS,i+1);
   if shortq=0 or d.get_object('metadata').get_number('allow_partial')=1 then
    detail:=json_object_t();detail.put('reservation_scope','QTY');detail.put('task_id',y.get_number('task'));detail.put('production_order_id',doc);detail.put('batch_id',to_char(pal.PRIHOD_NAKLAD_ID));
    RRL_STOCK_RESERVE_CORE.create_hard(y.get_number('reservation'),pal.UID_PALLET,y.get_string('cell'),qty,x.get_string('base'),y.get_number('uom_version'),'PRODUCTION_ORDER',doc,x.get_number('line'),'MES_RAW',p_actor,detail.to_clob);
    unitkeys:=RRL_STOCK_UNIT_CORE.automatic_units(pal.UID_PALLET,y.get_string('cell'),qty);RRL_STOCK_UNIT_CORE.reserve_units(pal.UID_PALLET,y.get_string('cell'),y.get_number('reservation'),qty,unitkeys);
    insert into RRL_MES_RAW_TRANSFER_TASK(TASK_ID,PRODUCTION_ORDER_ID,ORDER_LINE_ID,BOM_ID,BOM_LINE_ID,RAW_ARTICUL,RAW_BATCH_ID,BATCH_ID,UID_PALLET,SSCC,FROM_WARE_ID,FROM_CELL,TO_WARE_ID,TO_CELL,REQUIRED_QTY,TASK_QTY,UNIT_CODE,RESERVATION_ID,TASK_STATUS,PRIORITY,CREATED_BY)
     values(y.get_number('task'),doc,x.get_number('line'),x.get_number('bom'),x.get_number('bom_line'),x.get_string('article'),pal.PRIHOD_NAKLAD_ID,to_char(pal.PRIHOD_NAKLAD_ID),pal.UID_PALLET,pal.SSCC,y.get_number('ware'),y.get_string('cell'),v.get_number('warehouse'),v.get_string('target'),nonnegative(x.get_string('required')),qty,x.get_string('base'),y.get_number('reservation'),'PLANNED',100,p_actor);
    insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,PRODUCTION_ORDER_ID,RAW_ARTICUL,UID_PALLET,SSCC,FROM_WARE_ID,FROM_CELL,TO_WARE_ID,TO_CELL,QTY,UNIT_CODE,QTY_MODE,PRIORITY,STATUS,CREATED_AT,CREATED_BY)
     values(y.get_number('warehouse_task'),'RAW_TO_PRODUCTION','MES_RAW_SUPPLY',y.get_number('task'),'PRODUCTION_ORDER',doc,doc,x.get_string('article'),pal.UID_PALLET,pal.SSCC,y.get_number('ware'),y.get_string('cell'),v.get_number('warehouse'),v.get_string('target'),qty,x.get_string('base'),'QTY',100,'PLANNED',systimestamp,p_actor);cnt:=cnt+1;
   end if;
  end loop;
  if cnt>0 then update RRL_PRODUCTION_ORDER set STATUS=case when STATUS='DRAFT' then 'RELEASED' else STATUS end,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where PRODUCTION_ORDER_ID=doc;end if;
  result.put('operation_id',d.get_string('operation_id'));result.put('task_count',cnt);result.put('shortage_count',shortq);p_result:=result.to_clob;
 end;
end;
/
