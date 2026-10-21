create or replace package body RRL_TRADE_DOCUMENT_API as
 procedure fail(p_reason varchar2) is begin raise_application_error(-20901,p_reason);end;
 procedure authorize(p_ware number,p_actor nvarchar2,p_permission varchar2) is begin
  lock table RRL_ACCESS_REV in share mode wait 5;
  RRL_ACCESS_API.assert_allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware,'TM9'));
 end;
 function document_body(p_ware number,p_kind varchar2,p_id varchar2) return json_object_t is v clob;j json_object_t;
 begin
  select BODY_JSON into v from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE=p_kind and EXTERNAL_ID=p_id and STATUS='ACCEPTED';
  j:=json_object_t.parse(v);
  if j.has('active') and not j.get_boolean('active') then fail('MASTER_INACTIVE:'||p_kind||':'||p_id);end if;
  return j;
 exception when no_data_found then fail('MASTER_MISSING:'||p_kind||':'||p_id);return null;
 end;
 function assigned(p_ware number,p_order varchar2,p_line varchar2,p_exclude varchar2 default null) return number is n number;
 begin
  select nvl(sum(x.qty),0) into n from RRL_TRADE_DOCUMENT d,
   json_table(d.BODY_JSON,'$.orders[*]' columns(order_id varchar2(100) path '$.order_id',line_id varchar2(100) path '$.line_id',qty number path '$.quantity'))x
   where d.WARE_ID=p_ware and d.ENTITY_TYPE='TRIP' and d.STATUS='ACCEPTED'
    and(p_exclude is null or d.EXTERNAL_ID<>p_exclude) and x.order_id=p_order and x.line_id=p_line;
  return n;
 end;
 procedure validate_payload(p_ware number,p_kind varchar2,p_id varchar2,b json_object_t) is
  a json_array_t;v json_object_t;r json_object_t;s json_object_t;owners json_array_t;prices json_array_t;items json_array_t;
  profile_value json_object_t;sku_value json_object_t;allow_broken boolean;allow_partial boolean;
  previous_body clob;current_body clob;supply_order varchar2(100);supply_line varchar2(100);buyout_used number;buyout_qty number;buyout_sku varchar2(100);buyout_target varchar2(100);buyout_mrc number;buyout_mode varchar2(20);mapped_article varchar2(160);received_article varchar2(160);found boolean;qty number;n number;owner_id varchar2(100);line_id varchar2(100);order_id varchar2(100);v_plan_mode varchar2(12);
 begin
  if p_kind='NEED' then
   r:=document_body(p_ware,'RECIPIENT',b.get_string('recipient_id'));
   s:=document_body(p_ware,'SKU',b.get_string('sku_id'));
   order_id:=b.get_string('recipient_id');
   select VERSION_NO into n from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='RECIPIENT'and EXTERNAL_ID=order_id;
   if n<>b.get_number('recipient_version')then fail('NEED_RECIPIENT_VERSION_CHANGED');end if;
   order_id:=b.get_string('sku_id');
   select VERSION_NO into n from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='SKU'and EXTERNAL_ID=order_id;
   if n<>b.get_number('sku_version')then fail('NEED_SKU_VERSION_CHANGED');end if;
   if b.get_string('uom')not in('EA','BOX')or nvl(b.get_number('forecast_quantity'),-1)<0 or nvl(b.get_number('target_quantity'),-1)<0 or nvl(b.get_number('available_quantity'),-1)<0 or not b.get_boolean('received_in_available')then fail('NEED_SNAPSHOT_INVALID');end if;
   a:=b.get_array('supplies');if a.get_size>200 then fail('NEED_SUPPLY_LIMIT');end if;
   for i in 0..a.get_size-1 loop
    v:=treat(a.get(i)as json_object_t);
    if v.get_string('uom')not in('EA','BOX')or nvl(v.get_number('quantity'),-1)<0 or nvl(v.get_number('version'),0)<1 or v.get_string('status')not in('PLANNED','IN_TRANSIT','RECEIVED','CANCELLED')then fail('NEED_SUPPLY_INVALID');end if;
   end loop;
   begin
    select BODY_JSON into previous_body from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='NEED'and EXTERNAL_ID=p_id;
    profile_value:=json_object_t.parse(previous_body);
    if profile_value.get_string('recipient_id')<>b.get_string('recipient_id')or profile_value.get_string('sku_id')<>b.get_string('sku_id')or profile_value.get_string('period_from')<>b.get_string('period_from')or profile_value.get_string('period_until')<>b.get_string('period_until')then fail('NEED_IDENTITY_CHANGED');end if;
   exception when no_data_found then null;end;
  elsif p_kind='SKU' then
   mapped_article:=b.get_string('wms_article_id');
   if mapped_article is not null then
    select count(*)into n from RRL_ARTICULS where ACTICUL=mapped_article;
    if n<>1 then fail('WMS_ARTICLE_MAPPING_NOT_FOUND');end if;
   end if;
  elsif p_kind='SUPPLY' then
   s:=document_body(p_ware,'SKU',b.get_string('sku_id'));r:=document_body(p_ware,'OWNER',b.get_string('owner_id'));
   mapped_article:=b.get_string('wms_article_id');
   if mapped_article is null or s.get_string('wms_article_id')is null or mapped_article<>s.get_string('wms_article_id')then fail('SUPPLY_ARTICLE_MAPPING_MISMATCH');end if;
   supply_order:=b.get_string('sap_order_id');supply_line:=b.get_string('sap_line_id');
   select l.ARTICUL into received_article from RRL_SAP_SUPPLY_ORDER h join RRL_SAP_SUPPLY_LINE l on l.ORDER_ID=h.ORDER_ID
    where h.ORDER_ID=supply_order and h.WARE_ID=p_ware and l.LINE_NUMBER=supply_line;
   if received_article<>mapped_article then fail('SUPPLY_LINE_ARTICLE_MISMATCH');end if;
   prices:=s.get_array('permitted_mrc');found:=false;
   for k in 0..prices.get_size-1 loop if prices.get_number(k)=b.get_number('mrc')then found:=true;end if;end loop;
   if not found then fail('SUPPLY_MRC_NOT_PERMITTED');end if;
  elsif p_kind='RECIPIENT' then
   if b.get_number('wms_customer_id')is not null then
    qty:=b.get_number('wms_customer_id');
    select count(*)into n from RRL_CUSTOMER where CUSTOMER_ID=qty and ACTIVE=1;
    if n<>1 then fail('WMS_CUSTOMER_MAPPING_NOT_FOUND');end if;
   end if;
   v:=document_body(p_ware,'OWNER',b.get_string('target_owner_id'));a:=b.get_array('permitted_source_owners');
   for i in 0..a.get_size-1 loop v:=document_body(p_ware,'OWNER',a.get_string(i));end loop;
  elsif p_kind='ORDER' then
   select count(*)into n from RRL_TRADE_BUYOUT where WARE_ID=p_ware and BASIS_ORDER_ID=p_id and REQUESTED_UNITS>REJECTED_UNITS;
   if n>0 and b.get_string('order_kind')<>'BUYOUT'then fail('BUYOUT_BASIS_KIND_IMMUTABLE');end if;
   if b.get_string('order_kind')='BUYOUT'then
    buyout_mode:=b.get_string('buyout_mode');
    if buyout_mode is null or buyout_mode not in('BEFORE_PICK','AFTER_PICK','IN_TRANSIT')then fail('BUYOUT_MODE_REQUIRED');end if;
   end if;
   r:=document_body(p_ware,'RECIPIENT',b.get_string('recipient_id'));owners:=r.get_array('permitted_source_owners');
   if b.get_string('order_kind')='TOPUP' then v:=document_body(p_ware,'TRIP',b.get_string('parent_trip_id'));end if;
   current_body:=b.to_clob;
   select count(*)into n from RRL_TRADE_DOCUMENT d,
    json_table(d.BODY_JSON,'$.orders[*]' columns(order_id varchar2(100) path '$.order_id',line_id varchar2(100) path '$.line_id'))x
    where d.WARE_ID=p_ware and d.ENTITY_TYPE='TRIP' and d.STATUS='ACCEPTED' and x.order_id=p_id
     and not exists(select 1 from json_table(current_body,'$.lines[*]' columns(line_id varchar2(100) path '$.line_id'))y where y.line_id=x.line_id);
   if n>0 then fail('ASSIGNED_LINE_REMOVAL_REQUIRES_CHANGE');end if;
   a:=b.get_array('lines');
   for i in 0..a.get_size-1 loop
    v:=treat(a.get(i)as json_object_t);s:=document_body(p_ware,'SKU',v.get_string('sku_id'));
    owner_id:=v.get_string('source_owner_id');found:=false;
    for k in 0..owners.get_size-1 loop if owners.get_string(k)=owner_id then found:=true;end if;end loop;
    if not found then fail('SOURCE_OWNER_NOT_PERMITTED');end if;
    s:=document_body(p_ware,'OWNER',owner_id);s:=document_body(p_ware,'OWNER',v.get_string('target_owner_id'));
    if v.get_string('target_owner_id')<>r.get_string('target_owner_id') then fail('TARGET_OWNER_MISMATCH');end if;
    s:=document_body(p_ware,'SKU',v.get_string('sku_id'));prices:=s.get_array('permitted_mrc');found:=false;
    for k in 0..prices.get_size-1 loop if prices.get_number(k)=v.get_number('mrc') then found:=true;end if;end loop;
    if not found then fail('MRC_NOT_PERMITTED');end if;
    if v.get_number('quantity')<=0 or trunc(v.get_number('quantity'))<>v.get_number('quantity') then fail('WHOLE_UNIT_REQUIRED');end if;
    allow_broken:=false;if r.has('allow_broken_box')then allow_broken:=r.get_boolean('allow_broken_box');end if;
    if b.get_string('order_kind')<>'BUYOUT'and(allow_broken is null or not allow_broken)and v.get_string('uom')='EA'and mod(v.get_number('quantity'),s.get_number('units_per_box'))<>0 then fail('BROKEN_BOX_NOT_ALLOWED');end if;
    if v.get_number('min_osg_days')<r.get_number('min_osg_days') then fail('OSG_BELOW_RECIPIENT');end if;
    if b.get_string('order_kind')='BUYOUT'then
     if v.get_string('uom')<>'EA'then fail('BUYOUT_BASE_UNIT_REQUIRED');end if;
     buyout_qty:=v.get_number('quantity');buyout_sku:=v.get_string('sku_id');buyout_target:=v.get_string('target_owner_id');buyout_mrc:=v.get_number('mrc');line_id:=v.get_string('line_id');
     select nvl(sum(REQUESTED_UNITS-REJECTED_UNITS),0)into buyout_used from RRL_TRADE_BUYOUT where WARE_ID=p_ware and BASIS_ORDER_ID=p_id and BASIS_LINE_ID=line_id;
     if buyout_qty<buyout_used then fail('BUYOUT_BASIS_QUANTITY_ALREADY_USED');end if;
     select count(*)into n from RRL_TRADE_BUYOUT where WARE_ID=p_ware and BASIS_ORDER_ID=p_id and BASIS_LINE_ID=line_id and REQUESTED_UNITS>REJECTED_UNITS
      and(SKU_ID<>buyout_sku or SOURCE_OWNER_ID<>owner_id or TARGET_OWNER_ID<>buyout_target or MRC<>buyout_mrc or BUYOUT_MODE<>buyout_mode);
     if n>0 then fail('BUYOUT_BASIS_LINE_ALREADY_USED');end if;
    end if;
    n:=assigned(p_ware,p_id,v.get_string('line_id'));
    if n>v.get_number('quantity') or(b.get_boolean('cancelled') and n>0) then fail('ORDER_ASSIGNED_NEEDS_CHANGE');end if;
   end loop;
   select count(*)into n from RRL_TRADE_BUYOUT bo where WARE_ID=p_ware and BASIS_ORDER_ID=p_id and REQUESTED_UNITS>REJECTED_UNITS
    and not exists(select 1 from json_table(current_body,'$.lines[*]'columns(LINE_VALUE varchar2(100)path'$.line_id'))x where x.LINE_VALUE=bo.BASIS_LINE_ID);
   if n>0 then fail('BUYOUT_BASIS_LINE_REMOVAL_REQUIRES_CHANGE');end if;
  elsif p_kind='TRIP' then
   select PLANNING_SOURCE into v_plan_mode from RRL_TRADE_SITE where WARE_ID=p_ware;
   if b.get_string('planning_source')<>v_plan_mode then fail('PLANNING_SOURCE_MISMATCH');end if;
   a:=b.get_array('orders');
   for i in 0..a.get_size-1 loop
    v:=treat(a.get(i)as json_object_t);order_id:=v.get_string('order_id');line_id:=v.get_string('line_id');
    r:=document_body(p_ware,'ORDER',order_id);if r.get_string('order_kind')='BUYOUT'then fail('BUYOUT_BASIS_IS_NOT_SHIPMENT');end if;items:=r.get_array('lines');found:=false;
    for k in 0..items.get_size-1 loop
     s:=treat(items.get(k)as json_object_t);
     if s.get_string('line_id')=line_id then
      found:=true;qty:=v.get_number('quantity');
      if qty<=0 or trunc(qty)<>qty or qty+assigned(p_ware,order_id,line_id,p_id)>s.get_number('quantity') then fail('ORDER_QUANTITY_ALREADY_ASSIGNED');end if;
      profile_value:=document_body(p_ware,'RECIPIENT',r.get_string('recipient_id'));allow_partial:=false;allow_broken:=false;
      if profile_value.has('allow_partial_ship')then allow_partial:=profile_value.get_boolean('allow_partial_ship');end if;
      if profile_value.has('allow_broken_box')then allow_broken:=profile_value.get_boolean('allow_broken_box');end if;
      if qty<s.get_number('quantity')and(allow_partial is null or not allow_partial)then fail('PARTIAL_SHIPMENT_NOT_ALLOWED');end if;
      sku_value:=document_body(p_ware,'SKU',s.get_string('sku_id'));
      if s.get_string('uom')='EA'and(allow_broken is null or not allow_broken)and mod(qty,sku_value.get_number('units_per_box'))<>0 then fail('BROKEN_BOX_NOT_ALLOWED');end if;
     end if;
    end loop;
    if not found then fail('ORDER_LINE_MISSING');end if;
   end loop;
  end if;
 end;
 procedure record_message(p_ware number,p_source varchar2,p_event varchar2,p_kind varchar2,p_id varchar2,p_version number,
  p_hash varchar2,p_business varchar2,p_json clob,p_result clob,p_actor nvarchar2) is begin
  insert into RRL_TRADE_MESSAGE(WARE_ID,SOURCE_ID,EVENT_ID,ENTITY_TYPE,EXTERNAL_ID,VERSION_NO,PAYLOAD_HASH,BUSINESS_HASH,REQUEST_JSON,RESULT_JSON,ACTOR)
   values(p_ware,p_source,p_event,p_kind,p_id,p_version,p_hash,p_business,p_json,p_result,p_actor);
 end;
 procedure configure(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob) is
  j json_object_t:=json_object_t.parse(p_json);previous_site RRL_TRADE_SITE%rowtype;h varchar2(64);v_id varchar2(100);n number;
  out_j json_object_t:=json_object_t();previous_result clob;prior_hash varchar2(64);prior_actor varchar2(50);
  v_source varchar2(100);v_skm varchar2(100);v_plan varchar2(12);v_enabled number;v_reason varchar2(2000);
 begin
  authorize(p_ware,p_actor,'warehouse_settings_edit');v_id:=j.get_string('operation_id');h:=j.get_string('payload_hash');
  v_source:=j.get_string('source_id');v_skm:=j.get_string('active_skm');v_plan:=j.get_string('planning_source');
  v_reason:=j.get_string('reason');v_enabled:=case when j.get_boolean('enabled')then 1 else 0 end;
  select ID into n from RRL_WARES where ID=p_ware for update wait 5;
  begin
   select PAYLOAD_HASH,RESULT_JSON,ACTOR into prior_hash,previous_result,prior_actor from RRL_TRADE_MESSAGE where WARE_ID=p_ware and SOURCE_ID='#CONFIG' and EVENT_ID=v_id;
   if prior_hash<>h or prior_actor<>p_actor then fail('OPERATION_CONFLICT');end if;
   out_j:=json_object_t.parse(previous_result);out_j.put('replayed',true);p_result:=out_j.to_clob;return;
  exception when no_data_found then null;end;
  begin select * into previous_site from RRL_TRADE_SITE where WARE_ID=p_ware for update wait 5;exception when no_data_found then previous_site.VERSION_NO:=0;end;
  if j.get_number('expected_version')<>previous_site.VERSION_NO then fail('VERSION_CONFLICT');end if;
  if previous_site.VERSION_NO>0 and v_source<>previous_site.SOURCE_ID then
   select count(*)into n from RRL_TRADE_DOCUMENT where WARE_ID=p_ware;
   if n=0 then select count(*)into n from RRL_TRADE_DEFERRED where WARE_ID=p_ware;end if;
   if n>0 then fail('SOURCE_IN_USE');end if;
  end if;
  if previous_site.VERSION_NO>0 and v_skm<>previous_site.ACTIVE_SKM then
   select count(*)into n from RRL_TRADE_BUYOUT where WARE_ID=p_ware and PENDING_UNITS>0;
   if n>0 then fail('OPEN_BUYOUTS_REQUIRE_SKM_RECONCILIATION');end if;
  end if;
  merge into RRL_TRADE_SITE d using(select p_ware WARE_ID from dual)x on(d.WARE_ID=x.WARE_ID)
   when matched then update set SOURCE_ID=v_source,ACTIVE_SKM=v_skm,PLANNING_SOURCE=v_plan,ENABLED=v_enabled,
    VERSION_NO=previous_site.VERSION_NO+1,REASON=v_reason,CHANGED_BY=p_actor,CHANGED_AT=systimestamp
   when not matched then insert(WARE_ID,SOURCE_ID,ACTIVE_SKM,PLANNING_SOURCE,ENABLED,VERSION_NO,REASON,CHANGED_BY)
    values(p_ware,v_source,v_skm,v_plan,v_enabled,1,v_reason,p_actor);
  out_j.put('warehouse_id',p_ware);out_j.put('version',previous_site.VERSION_NO+1);out_j.put('replayed',false);out_j.put('stock_changed',false);p_result:=out_j.to_clob;
  record_message(p_ware,'#CONFIG',v_id,'SITE',to_char(p_ware,'TM9'),previous_site.VERSION_NO+1,h,h,p_json,p_result,p_actor);
 end;
 procedure receive_impl(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob,p_resume boolean) is
  j json_object_t:=json_object_t.parse(p_json);b json_object_t:=j.get_object('payload');site RRL_TRADE_SITE%rowtype;
  v_id varchar2(100);v_kind varchar2(12);v_event varchar2(100);h varchar2(64);bh varchar2(64);v_version number;
  prior_hash varchar2(64);previous_result clob;old_version number;old_hash varchar2(64);old_scan timestamp with time zone;old_status varchar2(12);
  out_j json_object_t:=json_object_t();new_status varchar2(12):='ACCEPTED';body clob;outbox_id number;outcome varchar2(12):='ACCEPTED';error_code varchar2(500);response_key varchar2(80);
 begin
  authorize(p_ware,p_actor,'tradecase_import');
  select * into site from RRL_TRADE_SITE where WARE_ID=p_ware for update wait 5;
  if b.get_string('entity_type')='ORDER'and b.get_string('order_kind')='BUYOUT'then
   RRL_ACCESS_API.assert_allowed(p_actor,'tradecase_buyout_basis_import','WAREHOUSE',to_char(p_ware,'TM9'));
  end if;
  if site.ENABLED<>1 then fail('SITE_DISABLED');end if;
  if j.get_string('source_id')<>site.SOURCE_ID or j.get_number('warehouse_id')<>p_ware then fail('SOURCE_MISMATCH');end if;
  v_event:=j.get_string('event_id');v_id:=j.get_string('document_id');v_kind:=b.get_string('entity_type');v_version:=j.get_number('version');
  h:=j.get_string('payload_hash');bh:=j.get_string('business_hash');
  begin
   select PAYLOAD_HASH,RESULT_JSON into prior_hash,previous_result from RRL_TRADE_MESSAGE where WARE_ID=p_ware and SOURCE_ID=site.SOURCE_ID and EVENT_ID=v_event;
   if prior_hash<>h then fail('EVENT_CONTENT_CONFLICT');end if;
   if not p_resume then out_j:=json_object_t.parse(previous_result);out_j.put('replayed',true);p_result:=out_j.to_clob;return;end if;
  exception when no_data_found then null;end;
  if p_resume then
   select STATE,RESULT_JSON into outcome,p_result from RRL_TRADE_DEFERRED
    where WARE_ID=p_ware and SOURCE_ID=site.SOURCE_ID and EVENT_ID=v_event for update wait 5;
   if outcome<>'WAITING' then return;end if;outcome:='ACCEPTED';
  end if;
  begin select VERSION_NO,CONTENT_HASH,FIRST_SCAN_AT,STATUS into old_version,old_hash,old_scan,old_status from RRL_TRADE_DOCUMENT
   where WARE_ID=p_ware and ENTITY_TYPE=v_kind and EXTERNAL_ID=v_id;
  exception when no_data_found then old_version:=0;end;
  savepoint trade_document_apply;
  begin
  if v_version<old_version then fail('STALE_VERSION');end if;
  if v_version=old_version and bh<>old_hash then fail('VERSION_CONTENT_CONFLICT');end if;
  if v_version>old_version then
   if old_status='CANCELLED' then fail('CANCELLED_DOCUMENT_REQUIRES_NEW_ID');end if;
   if old_scan is not null then fail('FIRST_SCAN_REQUIRES_REVERSE');end if;
   validate_payload(p_ware,v_kind,v_id,b);body:=b.to_clob;
   if b.has('cancelled') and b.get_boolean('cancelled') then new_status:='CANCELLED';end if;
   merge into RRL_TRADE_DOCUMENT d using(select p_ware WARE_ID,v_kind ENTITY_TYPE,v_id EXTERNAL_ID from dual)x
    on(d.WARE_ID=x.WARE_ID and d.ENTITY_TYPE=x.ENTITY_TYPE and d.EXTERNAL_ID=x.EXTERNAL_ID)
    when matched then update set SOURCE_ID=site.SOURCE_ID,VERSION_NO=v_version,CONTENT_HASH=bh,BODY_JSON=body,STATUS=new_status,CHANGED_BY=p_actor,CHANGED_AT=systimestamp
    when not matched then insert(WARE_ID,ENTITY_TYPE,EXTERNAL_ID,SOURCE_ID,VERSION_NO,CONTENT_HASH,BODY_JSON,STATUS,CHANGED_BY)
     values(p_ware,v_kind,v_id,site.SOURCE_ID,v_version,bh,body,new_status,p_actor);
  end if;
  exception when others then
   if sqlcode<>-20901 then raise;end if;
   error_code:=substr(regexp_replace(sqlerrm,'^ORA-[0-9]+: *',''),1,500);
   rollback to trade_document_apply;
   if error_code like 'MASTER_MISSING:%' then outcome:='WAITING';else outcome:='REJECTED';end if;
  end;
  out_j.put('warehouse_id',p_ware);out_j.put('document_id',v_id);out_j.put('entity_type',v_kind);out_j.put('version',v_version);
  out_j.put('status',outcome);out_j.put('replayed',v_version=old_version);out_j.put('stock_changed',false);out_j.put('physical_execution','NOT_STARTED');
  out_j.put('schema_version',1);out_j.put('event_id',v_event);out_j.put('correlation_id',v_event);out_j.put('source_id','WMS_TRADECASE');
  out_j.put('target_source_id',site.SOURCE_ID);out_j.put('occurred_at',to_char(systimestamp,'YYYY-MM-DD"T"HH24:MI:SS.FF3TZH:TZM'));
  out_j.put('external_delivery','PENDING');out_j.put('external_business','NOT_CONFIRMED');
  if error_code is not null then out_j.put('code',error_code);end if;
  if p_resume and outcome='WAITING' then
   -- An unsuccessful retry does not emit another acknowledgement or replace the original receipt.
   p_result:=out_j.to_clob;return;
  end if;
  select lower(rawtohex(standard_hash(to_char(p_ware,'TM9')||':'||site.SOURCE_ID||':'||v_event,'SHA256')))into response_key from dual;
  if p_resume then response_key:=response_key||':RESOLVED';out_j.put('response_kind','RESOLUTION');end if;
  outbox_id:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_DOCUMENT_RESPONSE','TRADE_'||v_kind,v_id,'TC:'||response_key,out_j.to_clob,'TRADECASE_BUS',v_event);
  out_j.put('outbox_id',outbox_id);p_result:=out_j.to_clob;
  if not p_resume then
  record_message(p_ware,site.SOURCE_ID,v_event,v_kind,v_id,v_version,h,bh,p_json,p_result,p_actor);
   if outcome='WAITING' then
    insert into RRL_TRADE_DEFERRED(WARE_ID,SOURCE_ID,EVENT_ID,RESULT_JSON,CHANGED_BY)
     values(p_ware,site.SOURCE_ID,v_event,p_result,p_actor);
   end if;
  end if;
 end;
 procedure receive_document(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob) is begin
  receive_impl(p_ware,p_actor,p_json,p_result,false);
 end;
 procedure retry_document(p_ware number,p_actor nvarchar2,p_event varchar2,p_result out clob) is
  request_json clob;source_value varchar2(100);result_value json_object_t;state_value varchar2(12);
 begin
  authorize(p_ware,p_actor,'tradecase_import');
  select SOURCE_ID into source_value from RRL_TRADE_SITE where WARE_ID=p_ware for update wait 5;
  select m.REQUEST_JSON into request_json from RRL_TRADE_MESSAGE m join RRL_TRADE_DEFERRED d
   on(d.WARE_ID=m.WARE_ID and d.SOURCE_ID=m.SOURCE_ID and d.EVENT_ID=m.EVENT_ID)
   where m.WARE_ID=p_ware and m.SOURCE_ID=source_value and m.EVENT_ID=p_event;
  receive_impl(p_ware,p_actor,request_json,p_result,true);
  result_value:=json_object_t.parse(p_result);state_value:=result_value.get_string('status');
  update RRL_TRADE_DEFERRED set STATE=state_value,RESULT_JSON=p_result,ATTEMPTS=ATTEMPTS+1,
   CHANGED_BY=p_actor,CHANGED_AT=systimestamp
   where WARE_ID=p_ware and SOURCE_ID=source_value and EVENT_ID=p_event and STATE='WAITING';
 end;
 procedure read_documents(p_ware number,p_actor nvarchar2,p_mode varchar2,p_kind varchar2,p_key varchar2,p_limit number,p_result out clob) is
  j json_object_t:=json_object_t();a json_array_t:=json_array_t();v json_object_t;site RRL_TRADE_SITE%rowtype;body clob;n number:=0;row_limit number:=p_limit+1;current_result clob;
 begin
  authorize(p_ware,p_actor,'tradecase_view');select * into site from RRL_TRADE_SITE where WARE_ID=p_ware;
  j.put('warehouse_id',p_ware);j.put('source_id',site.SOURCE_ID);j.put('active_skm',site.ACTIVE_SKM);
  j.put('planning_source',site.PLANNING_SOURCE);j.put('enabled',site.ENABLED=1);j.put('version',site.VERSION_NO);
  if p_mode='DETAIL' then
   select BODY_JSON,VERSION_NO into body,n from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE=p_kind and EXTERNAL_ID=p_key;
   j.put('payload',json_object_t.parse(body));j.put('document_version',n);j.put('document_id',p_key);j.put('entity_type',p_kind);
  elsif p_mode='LIST' then
   if p_limit<1 or p_limit>100 or p_limit<>trunc(p_limit) then fail('PAGE_LIMIT');end if;
   for d in(select EXTERNAL_ID,VERSION_NO,STATUS,BODY_JSON from RRL_TRADE_DOCUMENT
    where WARE_ID=p_ware and ENTITY_TYPE=p_kind and(p_key is null or EXTERNAL_ID>p_key)
    order by EXTERNAL_ID fetch first row_limit rows only)loop
    n:=n+1;if n>p_limit then j.put('has_more',true);exit;end if;
    v:=json_object_t();v.put('document_id',d.EXTERNAL_ID);v.put('version',d.VERSION_NO);v.put('status',d.STATUS);
    v.put('payload',json_object_t.parse(d.BODY_JSON));a.append(v);j.put('next_after',d.EXTERNAL_ID);
   end loop;
   if n<=p_limit then j.put('has_more',false);j.put_null('next_after');end if;j.put('items',a);
  elsif p_mode='MESSAGE' then
   select REQUEST_JSON,RESULT_JSON into body,p_result from RRL_TRADE_MESSAGE where WARE_ID=p_ware and SOURCE_ID=site.SOURCE_ID and EVENT_ID=p_key;
   j.put('request',json_object_t.parse(body));j.put('result',json_object_t.parse(p_result));
   begin select RESULT_JSON into current_result from RRL_TRADE_DEFERRED where WARE_ID=p_ware and SOURCE_ID=site.SOURCE_ID and EVENT_ID=p_key;
    j.put('current_result',json_object_t.parse(current_result));exception when no_data_found then null;end;
  elsif p_mode='MESSAGES' then
   if p_limit<1 or p_limit>100 or p_limit<>trunc(p_limit) then fail('PAGE_LIMIT');end if;
   for m in(select m.EVENT_ID,m.ENTITY_TYPE,m.EXTERNAL_ID,m.VERSION_NO,m.RESULT_JSON,d.RESULT_JSON CURRENT_RESULT
    from RRL_TRADE_MESSAGE m left join RRL_TRADE_DEFERRED d on(d.WARE_ID=m.WARE_ID and d.SOURCE_ID=m.SOURCE_ID and d.EVENT_ID=m.EVENT_ID)
    where m.WARE_ID=p_ware and m.SOURCE_ID=site.SOURCE_ID and(p_key is null or m.EVENT_ID>p_key)
    order by m.EVENT_ID fetch first row_limit rows only)loop
    n:=n+1;if n>p_limit then j.put('has_more',true);exit;end if;
    v:=json_object_t();v.put('event_id',m.EVENT_ID);v.put('entity_type',m.ENTITY_TYPE);v.put('document_id',m.EXTERNAL_ID);v.put('version',m.VERSION_NO);
    v.put('result',json_object_t.parse(m.RESULT_JSON));if m.CURRENT_RESULT is not null then v.put('current_result',json_object_t.parse(m.CURRENT_RESULT));end if;a.append(v);j.put('next_after',m.EVENT_ID);
   end loop;
   if n<=p_limit then j.put('has_more',false);j.put_null('next_after');end if;j.put('items',a);
  elsif p_mode<>'SITE' then fail('READ_MODE');end if;
  p_result:=j.to_clob;
 end;
end;
/
