package body RRL_STOCK_POOL_CMD as
 function nonnegative(p_text varchar2) return number is
 begin if p_text='0' then return 0;end if;return RRL_STOCK_MATH.quantity(p_text);end;
 function same_snapshot(a clob,b clob) return boolean is
 begin return dbms_crypto.hash(a,dbms_crypto.hash_sh256)=dbms_crypto.hash(b,dbms_crypto.hash_sh256);end;
 procedure compile_wave_pool(p_ware number,p_wave number,p_resources in out nocopy json_array_t,p_pools out json_array_t) is
  x json_object_t;rid number;qty number;ver number;flag number;
 begin
  p_pools:=json_array_t();
  for demand in(select pl.CUSTOMER_ORDER_ROW_ID,pr.ARTICUL,sum(pr.RESERVED_QTY) BASE_QTY
   from RRL_PICK_RESERVATION pr join RRL_PICK_WAVE_ORDER wo on wo.PICK_PLAN_ID=pr.PICK_PLAN_ID
   join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pr.PICK_PLAN_LINE_ID
   where wo.PICK_WAVE_ID=p_wave and wo.STATUS='ACTIVE' and pr.RESERVATION_STATUS='ACTIVE' and pr.RESERVATION_LEVEL='SOFT'
   group by pl.CUSTOMER_ORDER_ROW_ID,pr.ARTICUL order by pr.ARTICUL,pl.CUSTOMER_ORDER_ROW_ID) loop
   if p_pools.get_size>=200 then raise_application_error(-20881,'WAVE_POOL_BOUND_200');end if;
   RRL_STOCK_PLAN_HELPER.anchor(p_resources,20,'UNIQUE','SOFT.POOL:'||p_ware||':'||demand.ARTICUL);
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CUSTOMER_ORDER_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(demand.CUSTOMER_ORDER_ROW_ID));
   -- C-0157: a held SAP top-up row takes its own HARD over at launch (RRL_TRADE_TOPUP_ADOPT/adopt_hold); it has no common-pool share.
   if nvl(RRL_TRADE_TOPUP_ADOPT.line_proposal(demand.CUSTOMER_ORDER_ROW_ID),0)>0 then continue;end if;
   begin
    select RESERVATION_ID,QTY,RESERVATION_VERSION into rid,qty,ver from RRL_STOCK_RESERVATION
     where POOL_WARE_ID=p_ware and ARTICUL=demand.ARTICUL and SOURCE_LINE_ID=demand.CUSTOMER_ORDER_ROW_ID
      and RESERVATION_KIND='SOFT' and STATUS in('ACTIVE','ALLOCATED');
   exception when no_data_found then
    flag:=0;
    begin select nvl(SHIP_FROM_STOCK,case STOCK_ALLOC_CLASS when 'DRY_RACK' then 1 else 0 end) into flag
     from RRL_RECEIPT_SKU_RULE where WARE_ID=p_ware and ARTICUL=demand.ARTICUL;exception when no_data_found then null;end;
    if flag=1 then raise_application_error(-20886,'WAVE_COMMON_POOL_ALLOCATION_REQUIRED');end if;
    rid:=null;
   end;
   if rid is not null then
    if qty<demand.BASE_QTY then raise_application_error(-20886,'WAVE_EXCEEDS_COMMON_POOL_ALLOCATION');end if;
    RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(rid));
    x:=json_object_t();x.put('id',rid);x.put('version',ver);x.put('old_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));
    x.put('consume_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(demand.BASE_QTY));
    x.put('warehouse',p_ware);x.put('article',demand.ARTICUL);x.put('line_id',demand.CUSTOMER_ORDER_ROW_ID);p_pools.append(x);
   end if;
  end loop;
 end;
 procedure consume_wave_pool(p_pools json_array_t,p_actor varchar2) is
  x json_object_t;sr RRL_STOCK_RESERVATION%rowtype;rid number;qty number;left_qty number;
 begin
  for i in 0..p_pools.get_size-1 loop
   x:=treat(p_pools.get(i) as json_object_t);rid:=x.get_number('id');
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('UNIQUE','SOFT.POOL:'||x.get_number('warehouse')||':'||x.get_string('article')));
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=rid for update;
   if sr.RESERVATION_VERSION!=x.get_number('version') or sr.QTY!=RRL_STOCK_MATH.quantity(x.get_string('old_quantity'))
    or sr.STATUS not in('ACTIVE','ALLOCATED') or sr.RESERVATION_KIND!='SOFT'
    or sr.ARTICUL!=x.get_string('article') or sr.POOL_WARE_ID!=x.get_number('warehouse') or sr.SOURCE_LINE_ID!=x.get_number('line_id')
    then raise_application_error(-20890,'CLOSURE_CHANGED: wave common pool');end if;
   qty:=RRL_STOCK_MATH.quantity(x.get_string('consume_quantity'));left_qty:=sr.QTY-qty;
   if left_qty<0 then raise_application_error(-20886,'WAVE_EXCEEDS_COMMON_POOL_ALLOCATION');end if;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,rid);
   update RRL_STOCK_RESERVATION set QTY=left_qty,STATUS=case when left_qty=0 then 'CONSUMED' else 'ACTIVE' end,
    RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=rid;
   RRL_STOCK_CTX_API.end_effect;
  end loop;
 end;
 -- C-0160: trade plan proof. Every allocated row names quantities per physical class: each class is one this row accepts, every share is
 -- a whole pick step, the shares make the row's allocation, and no class is promised beyond its eligible quantity.
 procedure prove_trade(s json_object_t,h json_object_t,step number)is
  type num_map is table of number index by varchar2(400);used num_map;free num_map;
  a json_array_t:=s.get_array('orders');cls json_array_t:=s.get_array('classes');x json_object_t;src json_object_t;ls json_object_t;comp json_array_t;
  keys json_key_list;lid varchar2(40);qty number;q number;total number;ok boolean;key_value varchar2(400);
 begin
  if not h.has('sources')then raise_application_error(-20881,'POOL_TRADE_SOURCES_REQUIRED');end if;
  src:=h.get_object('sources');
  for i in 0..cls.get_size-1 loop x:=treat(cls.get(i) as json_object_t);free(x.get_string('key')):=nonnegative(x.get_string('free'));used(x.get_string('key')):=0;end loop;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);lid:=RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('line_id'));
   qty:=nonnegative(h.get_object('allocations').get_string(lid));total:=0;
   if qty>0 and x.has('pool_reason')then raise_application_error(-20881,'POOL_TRADE_LINE_NOT_ALLOCATABLE');end if;
   if src.has(lid)then
    ls:=src.get_object(lid);keys:=ls.get_keys;comp:=x.get_array('classes');
    for k in 1..keys.count loop
     key_value:=keys(k);q:=nonnegative(ls.get_string(key_value));ok:=false;
     if comp is not null then for c in 0..comp.get_size-1 loop if comp.get_string(c)=key_value then ok:=true;exit;end if;end loop;end if;
     if q>0 and(not ok or not used.exists(key_value))then raise_application_error(-20881,'POOL_TRADE_SOURCE_INCOMPATIBLE');end if;
     if mod(q,step)!=0 then raise_application_error(-20881,'POOL_ALLOCATION_INVALID');end if;
     if q>0 then used(key_value):=used(key_value)+q;end if;total:=total+q;
    end loop;
   end if;
   if total!=qty then raise_application_error(-20881,'POOL_TRADE_SOURCE_SPLIT_INVALID');end if;
  end loop;
  key_value:=used.first;
  while key_value is not null loop
   if used(key_value)>free(key_value)then raise_application_error(-20881,'POOL_TRADE_CLASS_OVERALLOCATED');end if;key_value:=used.next(key_value);
  end loop;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);h json_object_t;s json_object_t;v json_object_t:=json_object_t();x json_object_t;item json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();lines json_array_t:=json_array_t();a json_array_t;old json_array_t;
  raw_snapshot clob;current_snapshot clob;ware number;article varchar2(160);rid number;oid number;lid number;qty number;total number:=0;step number;available number;found boolean;
 begin
  if p_hints is null then raise_application_error(-20881,'POOL_TRUSTED_PLAN_REQUIRED');end if;
  h:=json_object_t.parse(p_hints);s:=d.get_object('source');ware:=s.get_number('warehouse');article:=s.get_string('article');
  if h.get_string('algorithm')!='PROPORTIONAL_WHOLE_STEP_V1' then raise_application_error(-20881,'POOL_ALGORITHM_REQUIRED');end if;
  raw_snapshot:=h.get_clob('snapshot');current_snapshot:=RRL_STOCK_POOL_READ.snapshot_json(ware,article);
  if not same_snapshot(raw_snapshot,current_snapshot) then raise_application_error(-20890,'CLOSURE_CHANGED: pool planning snapshot');end if;
  s:=json_object_t.parse(raw_snapshot);available:=nonnegative(s.get_string('available'));step:=RRL_STOCK_MATH.quantity(s.get_string('step'));
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.fence(f,'SKU',article);
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,20,'UNIQUE','SOFT.POOL:'||ware||':'||article);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),dbms_crypto.hash_sh256)));
  a:=s.get_array('stocks');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if nonnegative(x.get_string('free'))>0 then
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),article,x.get_string('cell'),null);
   end if;
  end loop;
  old:=s.get_array('reservations');
  for i in 0..old.get_size-1 loop
   x:=treat(old.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));
  end loop;
  a:=s.get_array('orders');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);oid:=x.get_number('order_id');lid:=x.get_number('line_id');
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(oid));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(lid));
   qty:=nonnegative(h.get_object('allocations').get_string(RRL_STOCK_PLAN_HELPER.decimal_text(lid)));
   if qty<0 or qty>nonnegative(x.get_string('quantity')) or mod(qty,step)!=0 then raise_application_error(-20881,'POOL_ALLOCATION_INVALID');end if;
   if s.get_number('from_stock')=0 and qty!=0 then raise_application_error(-20881,'POOL_PLANNED_RECEIPT_IS_NOT_STOCK');end if;
   total:=total+qty;rid:=null;
   for k in 0..old.get_size-1 loop
    item:=treat(old.get(k) as json_object_t);
    if item.get_number('line_id')=lid then rid:=item.get_number('id');exit;end if;
   end loop;
   if qty>0 and rid is null then select RRL_STOCK_RESERVATION_SQ.nextval into rid from dual;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(rid));end if;
   item:=json_object_t();item.put('order_id',oid);item.put('line_id',lid);item.put('customer_id',x.get_number('customer_id'));item.put('reservation_id',rid);
   item.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));lines.append(item);
  end loop;
  if total>available then raise_application_error(-20881,'POOL_OVERALLOCATED');end if;
  if nvl(s.get_number('trade'),0)=1 then prove_trade(s,h,step);v.put('sources',h.get_object('sources'));end if;
  v.put('snapshot',raw_snapshot);v.put('warehouse',ware);v.put('article',article);v.put('lines',lines);v.put('total',RRL_STOCK_PLAN_HELPER.decimal_text(total));
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;s json_object_t;x json_object_t;item json_object_t;j json_object_t:=json_object_t();
  a json_array_t;old json_array_t;lines json_array_t;wire clob;raw_snapshot clob;ware number;article varchar2(160);op varchar2(100);rid number;oid number;lid number;cid number;qty number;base varchar2(20);found boolean;dummy number;order_wire clob;
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_reservation_edit')!=1 then raise_application_error(-20882,'POOL_ALLOCATION_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(wire).get_object('domain');ware:=v.get_number('warehouse');article:=v.get_string('article');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('UNIQUE','SOFT.POOL:'||ware||':'||article));
  raw_snapshot:=v.get_clob('snapshot');s:=json_object_t.parse(raw_snapshot);a:=s.get_array('orders');order_wire:=a.to_clob;base:=s.get_string('unit');lines:=v.get_array('lines');old:=s.get_array('reservations');
  for row_id in(select CUSTOMER_ORDER_ID,CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW
    where CUSTOMER_ORDER_ROW_ID in(select ID from json_table(order_wire,'$[*]' columns(ID number path '$.line_id')))
    order by CUSTOMER_ORDER_ID,CUSTOMER_ORDER_ROW_ID) loop
   select CUSTOMER_ORDER_ID into dummy from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=row_id.CUSTOMER_ORDER_ID for update;
   select CUSTOMER_ORDER_ROW_ID into dummy from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=row_id.CUSTOMER_ORDER_ROW_ID for update;
  end loop;
  if not same_snapshot(raw_snapshot,RRL_STOCK_POOL_READ.snapshot_json(ware,article)) then raise_application_error(-20890,'CLOSURE_CHANGED: locked pool snapshot');end if;
  -- C-0160: today's operate right on the owner of every class this trade plan promises; the snapshot itself is reader-independent.
  if nvl(s.get_number('trade'),0)=1 then
   declare cls json_array_t:=s.get_array('classes');src json_object_t:=v.get_object('sources');ls json_object_t;keys json_key_list;c json_object_t;
   begin
    if src.get_size>0 then
    for i in 0..cls.get_size-1 loop
     c:=treat(cls.get(i) as json_object_t);
     keys:=src.get_keys;
     for k in 1..keys.count loop
      ls:=src.get_object(keys(k));
      if ls.has(c.get_string('key'))and nonnegative(ls.get_string(c.get_string('key')))>0 then
       RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,c.get_string('owner'),1);exit;
      end if;
     end loop;
    end loop;
    end if;
   end;
  end if;
  for i in 0..old.get_size-1 loop
   x:=treat(old.get(i) as json_object_t);rid:=x.get_number('id');found:=false;
   for k in 0..lines.get_size-1 loop
    item:=treat(lines.get(k) as json_object_t);
    if item.get_number('reservation_id')=rid and nonnegative(item.get_string('quantity'))>0 then found:=true;exit;end if;
   end loop;
   if not found then
    RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,rid);
    update RRL_STOCK_RESERVATION set QTY=0,STATUS='RELEASED',RESERVATION_VERSION=RESERVATION_VERSION+1,RELEASED_AT=systimestamp,RELEASED_BY=p_actor,RELEASE_REASON='Demand pool recalculation' where RESERVATION_ID=rid;
    RRL_STOCK_CTX_API.end_effect;
   end if;
  end loop;
  for i in 0..lines.get_size-1 loop
   x:=treat(lines.get(i) as json_object_t);rid:=x.get_number('reservation_id');oid:=x.get_number('order_id');lid:=x.get_number('line_id');cid:=x.get_number('customer_id');qty:=nonnegative(x.get_string('quantity'));
   if qty>0 then
    RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,rid);
    update RRL_STOCK_RESERVATION set QTY=qty,UNIT_CODE=base,STATUS='ACTIVE',RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=rid;
    if sql%rowcount=0 then
     insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,CUSTOMER_ID,CUSTOMER_ORDER_ID,POOL_WARE_ID,ARTICUL,QTY,UNIT_CODE,STATUS,PRIORITY,CREATED_BY,BASE_QTY,RESERVATION_VERSION)
      values(rid,'SOFT','QTY','PICKING','CUSTOMER_ORDER',oid,lid,cid,oid,ware,article,qty,base,'ACTIVE',100,p_actor,0,0);
    end if;
    RRL_STOCK_CTX_API.end_effect;
   end if;
  end loop;
  j.put('operation_id',op);j.put('warehouse',ware);j.put('article',article);j.put('unit',base);j.put('allocated_quantity',v.get_string('total'));j.put('available_quantity',s.get_string('available'));
  j.put('physical_reserve',false);j.put('from_stock',s.get_number('from_stock')=1);j.put('allocations',lines);p_result:=j.to_clob;
 end;
end;