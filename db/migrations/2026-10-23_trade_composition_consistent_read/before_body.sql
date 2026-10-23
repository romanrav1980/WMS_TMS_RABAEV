create or replace package body RRL_TRADE_COMPOSITION_API as
 procedure fail(p_reason varchar2)is begin raise_application_error(-20902,p_reason);end;
 function sha(p_text clob)return varchar2 is begin return lower(rawtohex(sys.dbms_crypto.hash(p_text,sys.dbms_crypto.hash_sh256)));end;

 -- Same order as the document intake: access revision, warehouse right, then the site row.
 function lock_site(p_ware number,p_actor nvarchar2,p_permission varchar2)return RRL_TRADE_SITE%rowtype is site RRL_TRADE_SITE%rowtype;
 begin
  lock table RRL_ACCESS_REV in share mode wait 5;
  RRL_ACCESS_API.assert_allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware,'TM9'));
  select*into site from RRL_TRADE_SITE where WARE_ID=p_ware for update wait 5;
  if site.ENABLED<>1 then fail('SITE_DISABLED');end if;
  return site;
 exception when no_data_found then fail('SITE_NOT_CONFIGURED');return site;
 end;

 function order_link(p_ware number,p_order varchar2)return RRL_TRADE_ORDER_LINK%rowtype is l RRL_TRADE_ORDER_LINK%rowtype;
 begin
  select*into l from RRL_TRADE_ORDER_LINK where WARE_ID=p_ware and EXTERNAL_ID=p_order;return l;
 exception when no_data_found then fail('TRADE_COMPOSITION_ORDER_NOT_BOUND');return l;
 end;

 -- Every owner of the order (source and target of each line) must be visible / operable: the same rule as the buyout parties.
 procedure require_owners(p_actor nvarchar2,p_ware number,p_order number,p_write number)is
 begin
  for o in(select SOURCE_OWNER_ID OWNER_ID from RRL_TRADE_ORDER_LINE where CUSTOMER_ORDER_ID=p_order
    union select TARGET_OWNER_ID from RRL_TRADE_ORDER_LINE where CUSTOMER_ORDER_ID=p_order)loop
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,o.OWNER_ID,p_write);
  end loop;
 end;

 -- Physical composition = the existing per-order fulfillment facts (RRL_CUSTOMER_ORDER_FULFILLMENT), the same rows the shipping/transport
 -- code uses: CASE pallets (PICKED_CASE_TASK_ID + PICKED_CONTENT_VERSION) and full pallets / warehouse tasks (PICKED_WAREHOUSE_TASK_ID +
 -- PICKED_STOCK_VERSION), with their fact quantity and FACT_COMPOSITION_JSON. No second versioning of HU membership: the signature is the
 -- SHA-256 of these fact lines only, so shipping (status, HU unlink after load) keeps it and a re-pick (new version) changes it.
 -- Closed = at least one fulfillment and every one PICKED or SHIPPED. Marked codes of the units in the CASE carrier lots and directly on
 -- picked pallets and their unit/code identities are part of the signed message.
 procedure compose(p_order number,p_items boolean,sig out varchar2,units out number,carriers out number,codes out number,closed out number,
                   items out json_array_t)is
  joined clob;u json_object_t;h json_array_t;f json_object_t;prev_key varchar2(64);prev_carrier varchar2(200);n_all number:=0;n_open number:=0;
  first boolean:=true;qty varchar2(60);
  procedure line(p varchar2)is begin
   if not first then dbms_lob.writeappend(joined,1,chr(10));end if;dbms_lob.writeappend(joined,length(p),p);first:=false;
  end;
 begin
  units:=0;carriers:=0;codes:=0;items:=json_array_t();
  dbms_lob.createtemporary(joined,true);
  for r in(select FULFILLMENT_ID,nvl(PICKED_PALLET_UID,PALLET_UID)CARRIER,STATUS,PICKED_CASE_TASK_ID,PICKED_CONTENT_VERSION,PICKED_WAREHOUSE_TASK_ID,
    PICKED_STOCK_VERSION,FACT_QTY,FACT_UOM,FACT_COMPOSITION_JSON from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=p_order order by FULFILLMENT_ID)loop
   n_all:=n_all+1;if n_all>1000 then fail('TRADE_COMPOSITION_FULFILLMENT_BOUND');end if;
   if r.STATUS not in('PICKED','SHIPPED')or(r.PICKED_CASE_TASK_ID is null and r.PICKED_WAREHOUSE_TASK_ID is null)then n_open:=n_open+1;
   else
    carriers:=carriers+1;qty:=RRL_STOCK_PLAN_HELPER.decimal_text(r.FACT_QTY);
    line('F|'||r.FULFILLMENT_ID||'|'||r.CARRIER||'|'||r.PICKED_CASE_TASK_ID||'|'||r.PICKED_CONTENT_VERSION||'|'||r.PICKED_WAREHOUSE_TASK_ID||'|'
     ||r.PICKED_STOCK_VERSION||'|'||qty||'|'||r.FACT_UOM||'|'||case when r.FACT_COMPOSITION_JSON is null then '-' else sha(r.FACT_COMPOSITION_JSON)end);
    if p_items then
     f:=json_object_t();f.put('kind','FULFILLMENT');f.put('fulfillment_id',r.FULFILLMENT_ID);f.put('carrier',r.CARRIER);f.put('case_task_id',r.PICKED_CASE_TASK_ID);
     f.put('content_version',r.PICKED_CONTENT_VERSION);f.put('warehouse_task_id',r.PICKED_WAREHOUSE_TASK_ID);f.put('stock_version',r.PICKED_STOCK_VERSION);
     f.put('fact_quantity',qty);f.put('fact_uom',r.FACT_UOM);
     if r.FACT_COMPOSITION_JSON is not null then f.put('fact_composition',json_element_t.parse(r.FACT_COMPOSITION_JSON));end if;
     items.append(f);
    end if;
   end if;
  end loop;
  closed:=case when n_all>0 and n_open=0 then 1 else 0 end;
  for r in(select x.CARRIER,un.PHYSICAL_UNIT_KEY UNIT_KEY,cd.CODE_HASH from(
     select nvl(fo.PICKED_PALLET_UID,fo.PALLET_UID)CARRIER,lot.LOT_UID UID_VALUE from RRL_CUSTOMER_ORDER_FULFILLMENT fo
      join RRL_CASE_CARRIER_LOT lot on lot.CASE_PICK_TASK_ID=fo.PICKED_CASE_TASK_ID where fo.CUSTOMER_ORDER_ID=p_order and fo.STATUS in('PICKED','SHIPPED')
     union select fo.PICKED_PALLET_UID,fo.PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT fo
      where fo.CUSTOMER_ORDER_ID=p_order and fo.STATUS in('PICKED','SHIPPED')and fo.PICKED_WAREHOUSE_TASK_ID is not null and fo.PICKED_PALLET_UID is not null)x
    join RRL_WMS_RECEIPT_UNIT un on un.CURRENT_UID=x.UID_VALUE
    left join RRL_WMS_RECEIPT_CODE cd on cd.UID_PALLET=un.UID_PALLET and cd.UNIT_ID=un.UNIT_ID
    order by x.CARRIER,un.PHYSICAL_UNIT_KEY,cd.CODE_HASH)loop
   line('U|'||r.CARRIER||'|'||r.UNIT_KEY||'|'||nvl(r.CODE_HASH,'-'));
   if prev_key is null or r.UNIT_KEY<>prev_key or r.CARRIER<>prev_carrier then
    units:=units+1;if units>10000 then fail('TRADE_COMPOSITION_UNIT_BOUND');end if;
    if p_items then
     if u is not null then u.put('code_hashes',h);items.append(u);end if;
     u:=json_object_t();u.put('kind','UNIT');u.put('carrier',r.CARRIER);u.put('physical_unit_key',r.UNIT_KEY);h:=json_array_t();
    end if;
    prev_key:=r.UNIT_KEY;prev_carrier:=r.CARRIER;
   end if;
   if r.CODE_HASH is not null then codes:=codes+1;if p_items then h.append(r.CODE_HASH);end if;end if;
  end loop;
  if p_items and u is not null then u.put('code_hashes',h);items.append(u);end if;
  if carriers>0 then sig:=sha(joined);end if;
  dbms_lob.freetemporary(joined);
 end;

 -- Stored snapshot + live reconciliation: why the order waits, what each system answered, and whether the physical facts still match.
 function card(c RRL_TRADE_ORDER_COMPOSITION%rowtype,l RRL_TRADE_ORDER_LINK%rowtype,site RRL_TRADE_SITE%rowtype,p_replayed boolean)return json_object_t is
  j json_object_t:=json_object_t();sig varchar2(64);units number;carriers number;codes number;closed number;items json_array_t;st varchar2(20);why varchar2(40);
 begin
  compose(l.CUSTOMER_ORDER_ID,false,sig,units,carriers,codes,closed,items);
  j.put('warehouse_id',l.WARE_ID);j.put('order_id',l.EXTERNAL_ID);j.put('order_version',l.DOCUMENT_VERSION);
  j.put('assembly_closed',closed=1);j.put('live_units',units);j.put('live_carriers',carriers);
  if c.COMPOSITION_NO is null then
   st:=case when closed=1 then 'NOT_REPORTED' else 'ASSEMBLY_OPEN' end;
  else
   j.put('composition_no',c.COMPOSITION_NO);j.put('signature',c.SIGNATURE);j.put('reported_order_version',c.ORDER_VERSION);
   j.put('units',c.UNIT_COUNT);j.put('carriers',c.CARRIER_COUNT);j.put('codes',c.CODE_COUNT);j.put('source_id',c.SOURCE_ID);j.put('skm_id',c.SKM_ID);
   j.put('sap_status',c.SAP_STATUS);j.put('sap_reason',c.SAP_REASON);j.put('skm_status',c.SKM_STATUS);j.put('skm_reason',c.SKM_REASON);
   j.put('composition_state',c.STATE);
   why:=case when closed<>1 then 'ASSEMBLY_REOPENED' when sig is null or sig<>c.SIGNATURE then 'COMPOSITION_CHANGED'
    when l.DOCUMENT_VERSION<>c.ORDER_VERSION then 'ORDER_VERSION_CHANGED' when c.SOURCE_ID<>site.SOURCE_ID then 'SOURCE_CHANGED'
    when c.SKM_STATUS='WAITING'and (case when c.SKM_ID=site.ACTIVE_SKM or(c.SKM_ID is null and site.ACTIVE_SKM is null)then 1 else 0 end)=0 then 'SKM_CHANGED' end;
   st:=case when why is not null then 'CHANGED' when 'REJECTED'in(c.SAP_STATUS,c.SKM_STATUS)then 'REJECTED'
    when 'WAITING'in(c.SAP_STATUS,c.SKM_STATUS)then 'WAITING' else 'CONFIRMED' end;
   j.put('change_reason',why);
  end if;
  j.put('status',st);if p_replayed then j.put('replayed',true);end if;
  return j;
 end;

 procedure report(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_json);ord varchar2(100):=j.get_string('order_id');
  site RRL_TRADE_SITE%rowtype;l RRL_TRADE_ORDER_LINK%rowtype;c RRL_TRADE_ORDER_COMPOSITION%rowtype;
  sig varchar2(64);units number;carriers number;codes number;closed number;items json_array_t;p json_object_t:=json_object_t();
  next_no number;body clob;skm_need varchar2(12);oid number;
 begin
  if ord is null or j.get_number('warehouse_id')<>p_ware then fail('TRADE_COMPOSITION_ORDER_REQUIRED');end if;
  site:=lock_site(p_ware,p_actor,'tradecase_order_bind');
  l:=order_link(p_ware,ord);
  require_owners(p_actor,p_ware,l.CUSTOMER_ORDER_ID,1);
  compose(l.CUSTOMER_ORDER_ID,true,sig,units,carriers,codes,closed,items);
  if closed<>1 then fail('TRADE_COMPOSITION_ASSEMBLY_OPEN');end if;
  begin
   select*into c from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=p_ware and ORDER_ID=ord and STATE='CURRENT'for update;
   -- The same physical composition, order version and recipients: a repeat (lost response, restart), not a second message.
   if c.SIGNATURE=sig and c.ORDER_VERSION=l.DOCUMENT_VERSION and c.SOURCE_ID=site.SOURCE_ID and (case when c.SKM_ID=site.ACTIVE_SKM or(c.SKM_ID is null and site.ACTIVE_SKM is null)then 1 else 0 end)=1 then
    p_result:=card(c,l,site,true).to_clob;return;
   end if;
   update RRL_TRADE_ORDER_COMPOSITION set STATE='SUPERSEDED',UPDATED_AT=systimestamp where WARE_ID=p_ware and ORDER_ID=ord and COMPOSITION_NO=c.COMPOSITION_NO;
  exception when no_data_found then null;
  end;
  if codes>0 and site.ACTIVE_SKM is null then fail('TRADE_COMPOSITION_SKM_NOT_CONFIGURED');end if;
  skm_need:=case when codes>0 then 'WAITING' else 'NOT_REQUIRED' end;
  select nvl(max(COMPOSITION_NO),0)+1 into next_no from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=p_ware and ORDER_ID=ord;
  p.put('schema','WMS_INTERNAL_COMPOSITION_V1');p.put('warehouse_id',p_ware);p.put('order_id',ord);p.put('order_version',l.DOCUMENT_VERSION);
  p.put('composition_no',next_no);p.put('signature',sig);p.put('source_id',site.SOURCE_ID);p.put('skm_id',site.ACTIVE_SKM);p.put('skm_required',codes>0);
  p.put('units',units);p.put('carriers',carriers);p.put('codes',codes);p.put('items',items);
  body:=p.to_clob;
  insert into RRL_TRADE_ORDER_COMPOSITION(WARE_ID,ORDER_ID,COMPOSITION_NO,ORDER_VERSION,CUSTOMER_ORDER_ID,SIGNATURE,UNIT_COUNT,CARRIER_COUNT,CODE_COUNT,
   SOURCE_ID,SKM_ID,SITE_VERSION,SAP_STATUS,SKM_STATUS,STATE,PAYLOAD_JSON,CREATED_BY)
   values(p_ware,ord,next_no,l.DOCUMENT_VERSION,l.CUSTOMER_ORDER_ID,sig,units,carriers,codes,site.SOURCE_ID,site.ACTIVE_SKM,site.VERSION_NO,
   'WAITING',skm_need,'CURRENT',body,p_actor);
  oid:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_COMPOSITION_REPORTED','TRADE_ORDER_COMPOSITION',ord,
   'TC:COMP:'||sha(p_ware||'|'||ord||'|'||next_no),body,'TRADECASE_BUS',to_char(next_no,'TM9'));
  update RRL_TRADE_ORDER_COMPOSITION set OUTBOX_ID=oid where WARE_ID=p_ware and ORDER_ID=ord and COMPOSITION_NO=next_no;
  select*into c from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=p_ware and ORDER_ID=ord and COMPOSITION_NO=next_no;
  p_result:=card(c,l,site,false).to_clob;
 end;

 procedure acknowledge(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_json);sys_code varchar2(3):=j.get_string('system_code');sender varchar2(100):=j.get_string('sender_id');
  ev varchar2(100):=j.get_string('event_id');ord varchar2(100):=j.get_string('order_id');cno number:=j.get_number('composition_no');
  sg varchar2(64):=j.get_string('signature');outcome varchar2(12):=j.get_string('outcome');rsn varchar2(2000):=substr(j.get_string('reason'),1,2000);
  ph varchar2(64):=j.get_string('payload_hash');
  site RRL_TRADE_SITE%rowtype;l RRL_TRADE_ORDER_LINK%rowtype;c RRL_TRADE_ORDER_COMPOSITION%rowtype;prior_ack RRL_TRADE_COMPOSITION_ACK%rowtype;
  sig varchar2(64);units number;carriers number;codes number;closed number;items json_array_t;cur_status varchar2(12);r json_object_t;reply clob;
 begin
  if j.get_number('warehouse_id')<>p_ware or sys_code is null or sys_code not in('SAP','SKM')or ev is null or sender is null or ph is null
   or outcome is null or outcome not in('ACCEPTED','REJECTED')or(outcome='REJECTED'and rsn is null)then fail('TRADE_COMPOSITION_ACK_INVALID');end if;
  site:=lock_site(p_ware,p_actor,'tradecase_import');
  l:=order_link(p_ware,ord);
  require_owners(p_actor,p_ware,l.CUSTOMER_ORDER_ID,1);  -- current rights also guard the stored receipt of a repeat
  begin
   select*into prior_ack from RRL_TRADE_COMPOSITION_ACK where WARE_ID=p_ware and SYSTEM_CODE=sys_code and SENDER_ID=sender and EVENT_ID=ev;
   if prior_ack.PAYLOAD_HASH<>ph then fail('TRADE_COMPOSITION_ACK_EVENT_CONFLICT');end if;
   r:=json_object_t.parse(prior_ack.RESULT_JSON);r.put('business_replayed',true);p_result:=r.to_clob;return;
  exception when no_data_found then null;
  end;
  begin select*into c from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=p_ware and ORDER_ID=ord and COMPOSITION_NO=cno for update;
  exception when no_data_found then fail('TRADE_COMPOSITION_NOT_FOUND');end;
  if c.STATE<>'CURRENT'then fail('TRADE_COMPOSITION_ACK_STALE');end if;  -- an answer to an older composition never confirms the new one
  if sg is null or sg<>c.SIGNATURE then fail('TRADE_COMPOSITION_SIGNATURE_MISMATCH');end if;
  if sys_code='SAP'then
   if sender<>c.SOURCE_ID or sender<>site.SOURCE_ID then fail('TRADE_COMPOSITION_SENDER_MISMATCH');end if;
   cur_status:=c.SAP_STATUS;
  else
   if c.SKM_STATUS='NOT_REQUIRED'then fail('TRADE_COMPOSITION_SKM_NOT_EXPECTED');end if;
   if sender<>c.SKM_ID then fail('TRADE_COMPOSITION_SENDER_MISMATCH');end if;
   if site.ACTIVE_SKM is null or sender<>site.ACTIVE_SKM then fail('TRADE_COMPOSITION_SKM_CHANGED');end if;  -- the former SKM after a switch
   cur_status:=c.SKM_STATUS;
  end if;
  compose(l.CUSTOMER_ORDER_ID,false,sig,units,carriers,codes,closed,items);
  if closed<>1 or sig is null or sig<>c.SIGNATURE or l.DOCUMENT_VERSION<>c.ORDER_VERSION then fail('TRADE_COMPOSITION_PHYSICAL_CHANGED');end if;
  if cur_status<>'WAITING'and cur_status<>outcome then fail('TRADE_COMPOSITION_ACK_FINAL');end if;
  if cur_status='WAITING'then
   if sys_code='SAP'then
    update RRL_TRADE_ORDER_COMPOSITION set SAP_STATUS=outcome,SAP_REASON=rsn,SAP_EVENT_ID=ev,UPDATED_AT=systimestamp
     where WARE_ID=p_ware and ORDER_ID=ord and COMPOSITION_NO=cno;
   else
    update RRL_TRADE_ORDER_COMPOSITION set SKM_STATUS=outcome,SKM_REASON=rsn,SKM_EVENT_ID=ev,UPDATED_AT=systimestamp
     where WARE_ID=p_ware and ORDER_ID=ord and COMPOSITION_NO=cno;
   end if;
   select*into c from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=p_ware and ORDER_ID=ord and COMPOSITION_NO=cno;
  end if;
  r:=card(c,l,site,false);r.put('acknowledged_system',sys_code);r.put('external_event_id',ev);r.put('stock_changed',false);reply:=r.to_clob;
  insert into RRL_TRADE_COMPOSITION_ACK(WARE_ID,SYSTEM_CODE,SENDER_ID,EVENT_ID,ORDER_ID,COMPOSITION_NO,OUTCOME,PAYLOAD_HASH,BODY_JSON,RESULT_JSON,ACTOR)
   values(p_ware,sys_code,sender,ev,ord,cno,outcome,ph,p_json,reply,p_actor);
  p_result:=reply;
 end;

 procedure orders(p_ware number,p_actor nvarchar2,p_limit number,p_result out clob)is
  a json_array_t:=json_array_t();r json_object_t:=json_object_t();n number:=0;site RRL_TRADE_SITE%rowtype;
  c RRL_TRADE_ORDER_COMPOSITION%rowtype;blank RRL_TRADE_ORDER_COMPOSITION%rowtype;l RRL_TRADE_ORDER_LINK%rowtype;
 begin
  RRL_ACCESS_API.assert_allowed(p_actor,'tradecase_view','WAREHOUSE',to_char(p_ware,'TM9'));
  if p_limit is null or p_limit<1 or p_limit>100 then fail('TRADE_COMPOSITION_LIMIT');end if;
  begin select*into site from RRL_TRADE_SITE where WARE_ID=p_ware;exception when no_data_found then fail('SITE_NOT_CONFIGURED');end;
  -- Orders of hidden owners are filtered before the bound: they are neither listed nor counted.
  for x in(select o.CUSTOMER_ORDER_ID from RRL_TRADE_ORDER_LINK o where o.WARE_ID=p_ware
    and(exists(select 1 from RRL_CASE_PICK_TASK ct where ct.CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID and ct.STATUS<>'CANCELLED')
     or exists(select 1 from RRL_PICK_TASK pt where pt.CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID and pt.TASK_TYPE='FULL_PALLET'and pt.STATUS<>'CANCELLED')
     or exists(select 1 from RRL_TRADE_ORDER_COMPOSITION s where s.WARE_ID=p_ware and s.ORDER_ID=o.EXTERNAL_ID))
    and not exists(select 1 from RRL_TRADE_ORDER_LINE ol where ol.CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID
     and(RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,ol.SOURCE_OWNER_ID,0)<>1 or RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,ol.TARGET_OWNER_ID,0)<>1))
    order by o.CUSTOMER_ORDER_ID desc fetch first 101 rows only)loop
   n:=n+1;if n>p_limit then r.put('has_more',true);exit;end if;
   select*into l from RRL_TRADE_ORDER_LINK where CUSTOMER_ORDER_ID=x.CUSTOMER_ORDER_ID;
   begin select*into c from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=p_ware and ORDER_ID=l.EXTERNAL_ID and STATE='CURRENT';
   exception when no_data_found then c:=blank;end;
   a.append(card(c,l,site,false));
  end loop;
  r.put('warehouse_id',p_ware);r.put('items',a);if not r.has('has_more')then r.put('has_more',false);end if;
  p_result:=r.to_clob;
 end;
end;
/
