create or replace package RRL_TRADE_SUPPLY_PARTS_API authid definer as
 -- C-0163: SUPPLY composition in parts. put_part / put_end record durably (END may arrive first: it repeats the header) and answer the transfer state;
 -- assembled returns the verified header and codes in part order for the caller to pass through the existing receive_document;
 -- mark_delivered records that outcome once. transfers lists transfers of visible owners (filtered before the bound).
 procedure put_part(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob);
 procedure put_end(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob);
 procedure assembled(p_ware number,p_actor nvarchar2,p_source varchar2,p_transfer varchar2,p_result out clob);
 procedure mark_delivered(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob);
 procedure transfers(p_ware number,p_actor nvarchar2,p_limit number,p_result out clob);
end;
/
create or replace package body RRL_TRADE_SUPPLY_PARTS_API as
 procedure fail(p_reason varchar2)is begin raise_application_error(-20901,p_reason);end;
 function sha(p_text clob)return varchar2 is begin return lower(rawtohex(sys.dbms_crypto.hash(p_text,sys.dbms_crypto.hash_sh256)));end;

 -- Same order as the document intake: access revision, warehouse right, then the site row; the source must be the site's source.
 function lock_site(p_ware number,p_actor nvarchar2,p_permission varchar2,p_source varchar2)return RRL_TRADE_SITE%rowtype is site RRL_TRADE_SITE%rowtype;
 begin
  lock table RRL_ACCESS_REV in share mode wait 5;
  RRL_ACCESS_API.assert_allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware,'TM9'));
  select*into site from RRL_TRADE_SITE where WARE_ID=p_ware for update wait 5;
  if site.ENABLED<>1 then fail('SITE_DISABLED');end if;
  if p_source is null or p_source<>site.SOURCE_ID then fail('SOURCE_MISMATCH');end if;
  return site;
 exception when no_data_found then fail('SITE_NOT_CONFIGURED');return site;
 end;

 -- Owner of the composition: the reader/sender must see it (the same rule as the documents of that owner).
 procedure require_owner(p_actor nvarchar2,p_ware number,p_header clob,p_write number)is
 begin RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,json_value(p_header,'$.owner_id'),p_write);end;

 -- A later version of the same document (as a transfer or an accepted document) makes an older part/END a no-op refusal.
 procedure assert_current(p_ware number,p_source varchar2,p_document varchar2,p_version number)is n number;
 begin
  select count(*)into n from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='SUPPLY'and EXTERNAL_ID=p_document and VERSION_NO>p_version;
  if n=0 then select count(*)into n from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware and SOURCE_ID=p_source and DOCUMENT_ID=p_document and VERSION_NO>p_version;end if;
  if n>0 then fail('SUPPLY_PART_VERSION_SUPERSEDED');end if;
 end;

 function state(p_ware number,p_source varchar2,p_transfer varchar2,p_replayed boolean)return clob is
  t RRL_TRADE_SUPPLY_TRANSFER%rowtype;j json_object_t:=json_object_t();m json_array_t:=json_array_t();
 begin
  select*into t from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware and SOURCE_ID=p_source and TRANSFER_ID=p_transfer;
  for x in(select level PART_NO from dual connect by level<=t.PART_COUNT
    minus select PART_NO from RRL_TRADE_SUPPLY_PART where WARE_ID=p_ware and SOURCE_ID=p_source and TRANSFER_ID=p_transfer order by 1)loop
   if m.get_size<50 then m.append(x.PART_NO);end if;
  end loop;
  j.put('warehouse_id',p_ware);j.put('source_id',p_source);j.put('transfer_id',p_transfer);j.put('document_id',t.DOCUMENT_ID);
  j.put('version',t.VERSION_NO);j.put('part_count',t.PART_COUNT);j.put('received_codes',t.RECEIVED_CODES);j.put('missing_parts',m);
  j.put('end_received',t.END_EVENT_ID is not null);j.put('status',t.STATUS);j.put('status_reason',t.STATUS_REASON);
  j.put('owner_id',json_value(t.HEADER_JSON,'$.owner_id'));j.put('delivered_event_id',t.DELIVERED_EVENT_ID);
  if p_replayed then j.put('replayed',true);end if;
  return j.to_clob;
 end;

 -- Completeness: every part 1..N, the END summary, and the same total and codes hash (codes joined by LF in part order).
 procedure evaluate(p_ware number,p_source varchar2,p_transfer varchar2)is
  t RRL_TRADE_SUPPLY_TRANSFER%rowtype;n number;total number:=0;joined clob;first boolean:=true;
 begin
  select*into t from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware and SOURCE_ID=p_source and TRANSFER_ID=p_transfer;
  if t.STATUS in('DELIVERED','DELIVERY_REJECTED','SUPERSEDED')then return;end if;
  select count(*),nvl(sum(CODE_COUNT),0)into n,total from RRL_TRADE_SUPPLY_PART where WARE_ID=p_ware and SOURCE_ID=p_source and TRANSFER_ID=p_transfer;
  if n<t.PART_COUNT or t.END_EVENT_ID is null then t.STATUS:='OPEN';t.STATUS_REASON:=case when t.END_EVENT_ID is null then 'WAITING_END'end;
  elsif total<>t.END_TOTAL then t.STATUS:='MISMATCH';t.STATUS_REASON:='TOTAL_MISMATCH:'||total||'/'||t.END_TOTAL;
  else
   dbms_lob.createtemporary(joined,true);
   for c in(select x.CODE from RRL_TRADE_SUPPLY_PART p,json_table(p.CODES_JSON,'$[*]'columns(SEQ for ordinality,CODE varchar2(4000)path'$.code'))x
     where p.WARE_ID=p_ware and p.SOURCE_ID=p_source and p.TRANSFER_ID=p_transfer order by p.PART_NO,x.SEQ)loop
    if not first then dbms_lob.writeappend(joined,1,chr(10));end if;dbms_lob.append(joined,c.CODE);first:=false;
   end loop;
   if sha(joined)<>t.END_CODES_SHA then t.STATUS:='MISMATCH';t.STATUS_REASON:='CODES_HASH_MISMATCH';else t.STATUS:='COMPLETE';t.STATUS_REASON:=null;end if;
   dbms_lob.freetemporary(joined);
  end if;
  update RRL_TRADE_SUPPLY_TRANSFER set STATUS=t.STATUS,STATUS_REASON=t.STATUS_REASON,RECEIVED_CODES=total,UPDATED_AT=systimestamp
   where WARE_ID=p_ware and SOURCE_ID=p_source and TRANSFER_ID=p_transfer;
 end;

 procedure put_part(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_json);site RRL_TRADE_SITE%rowtype;t RRL_TRADE_SUPPLY_TRANSFER%rowtype;
  src varchar2(100):=j.get_string('source_id');tr varchar2(100):=j.get_string('transfer_id');ev varchar2(100):=j.get_string('event_id');
  doc varchar2(100):=j.get_string('document_id');ver number:=j.get_number('version');part number:=j.get_number('part_no');cnt number:=j.get_number('part_count');
  ph varchar2(64):=j.get_string('part_hash');hh varchar2(64):=j.get_string('header_hash');header clob:=j.get_object('header').to_clob;
  codes clob:=j.get_array('codes').to_clob;ncodes number:=j.get_array('codes').get_size;prior_hash varchar2(64);prior_part number;total number;
 begin
  if j.get_number('warehouse_id')<>p_ware then fail('SOURCE_MISMATCH');end if;
  site:=lock_site(p_ware,p_actor,'tradecase_import',src);
  require_owner(p_actor,p_ware,header,1);
  select count(*)into total from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware and SOURCE_ID=src and END_EVENT_ID=ev;
  if total>0 then fail('SUPPLY_PART_EVENT_CONFLICT');end if;
  -- Exact replay of a recorded part (by event) answers the current transfer state; another body under that event is refused.
  begin select PART_HASH,PART_NO into prior_hash,prior_part from RRL_TRADE_SUPPLY_PART where WARE_ID=p_ware and SOURCE_ID=src and EVENT_ID=ev;
   if prior_hash<>ph then fail('SUPPLY_PART_EVENT_CONFLICT');end if;
   p_result:=state(p_ware,src,tr,true);return;
  exception when no_data_found then null;end;
  assert_current(p_ware,src,doc,ver);
  begin select*into t from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware and SOURCE_ID=src and TRANSFER_ID=tr for update;
   if t.DOCUMENT_ID<>doc or t.VERSION_NO<>ver or t.PART_COUNT<>cnt or t.HEADER_HASH<>hh then fail('SUPPLY_PART_HEADER_CONFLICT');end if;
  exception when no_data_found then
   insert into RRL_TRADE_SUPPLY_TRANSFER(WARE_ID,SOURCE_ID,TRANSFER_ID,DOCUMENT_ID,VERSION_NO,PART_COUNT,HEADER_JSON,HEADER_HASH,STATUS,CREATED_BY)
    values(p_ware,src,tr,doc,ver,cnt,header,hh,'OPEN',p_actor);
  end;
  -- Retransmission keeps its event id; another event cannot reuse the recorded part number.
  begin select PART_HASH into prior_hash from RRL_TRADE_SUPPLY_PART where WARE_ID=p_ware and SOURCE_ID=src and TRANSFER_ID=tr and PART_NO=part;
   fail('SUPPLY_PART_CONFLICT');
  exception when no_data_found then null;end;
  select nvl(sum(CODE_COUNT),0)into total from RRL_TRADE_SUPPLY_PART where WARE_ID=p_ware and SOURCE_ID=src and TRANSFER_ID=tr;
  if total+ncodes>10000 then fail('SUPPLY_PART_CODE_LIMIT');end if;
  insert into RRL_TRADE_SUPPLY_PART(WARE_ID,SOURCE_ID,TRANSFER_ID,PART_NO,EVENT_ID,PART_HASH,CODE_COUNT,CODES_JSON,ACTOR)
   values(p_ware,src,tr,part,ev,ph,ncodes,codes,p_actor);
  evaluate(p_ware,src,tr);
  p_result:=state(p_ware,src,tr,false);
 exception when dup_val_on_index then fail('SUPPLY_PART_CONFLICT');
 end;

 procedure put_end(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_json);site RRL_TRADE_SITE%rowtype;t RRL_TRADE_SUPPLY_TRANSFER%rowtype;
  src varchar2(100):=j.get_string('source_id');tr varchar2(100):=j.get_string('transfer_id');ev varchar2(100):=j.get_string('event_id');
  eh varchar2(64):=j.get_string('end_hash');tot number:=j.get_number('total_codes');csha varchar2(64):=j.get_string('codes_sha256');
  occ varchar2(40):=j.get_string('occurred_at');doc varchar2(100):=j.get_string('document_id');ver number:=j.get_number('version');
  cnt number:=j.get_number('part_count');hh varchar2(64):=j.get_string('header_hash');header clob:=j.get_object('header').to_clob;
  event_count number;
  -- JSON object methods never inside SQL (ORA-40573)
 begin
  if j.get_number('warehouse_id')<>p_ware then fail('SOURCE_MISMATCH');end if;
  site:=lock_site(p_ware,p_actor,'tradecase_import',src);
  require_owner(p_actor,p_ware,header,1);  -- END repeats the SUPPLY header, so the owner is known even before the first part
  select count(*)into event_count from RRL_TRADE_SUPPLY_PART where WARE_ID=p_ware and SOURCE_ID=src and EVENT_ID=ev;
  if event_count>0 then fail('SUPPLY_PART_EVENT_CONFLICT');end if;
  select count(*)into event_count from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware and SOURCE_ID=src and END_EVENT_ID=ev and TRANSFER_ID<>tr;
  if event_count>0 then fail('SUPPLY_PART_EVENT_CONFLICT');end if;
  begin select*into t from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware and SOURCE_ID=src and TRANSFER_ID=tr for update;
   if t.END_EVENT_ID is not null then
    if t.END_EVENT_ID=ev and t.END_HASH=eh then p_result:=state(p_ware,src,tr,true);return;end if;
    fail('SUPPLY_END_CONFLICT');
   end if;
   if t.DOCUMENT_ID<>doc or t.VERSION_NO<>ver or t.PART_COUNT<>cnt or t.HEADER_HASH<>hh then fail('SUPPLY_PART_HEADER_CONFLICT');end if;
   assert_current(p_ware,src,doc,ver);
   update RRL_TRADE_SUPPLY_TRANSFER set END_EVENT_ID=ev,END_HASH=eh,END_TOTAL=tot,END_CODES_SHA=csha,
    END_OCCURRED_AT=occ,UPDATED_AT=systimestamp where WARE_ID=p_ware and SOURCE_ID=src and TRANSFER_ID=tr;
  exception when no_data_found then
   -- END before any part is stored durably: the transfer starts with zero parts and every part is missing.
   assert_current(p_ware,src,doc,ver);
   insert into RRL_TRADE_SUPPLY_TRANSFER(WARE_ID,SOURCE_ID,TRANSFER_ID,DOCUMENT_ID,VERSION_NO,PART_COUNT,HEADER_JSON,HEADER_HASH,STATUS,CREATED_BY,
    END_EVENT_ID,END_HASH,END_TOTAL,END_CODES_SHA,END_OCCURRED_AT)values(p_ware,src,tr,doc,ver,cnt,header,hh,'OPEN',p_actor,ev,eh,tot,csha,occ);
  end;
  evaluate(p_ware,src,tr);
  p_result:=state(p_ware,src,tr,false);
 exception when dup_val_on_index then fail('SUPPLY_PART_EVENT_CONFLICT');
 end;

 procedure assembled(p_ware number,p_actor nvarchar2,p_source varchar2,p_transfer varchar2,p_result out clob)is
  t RRL_TRADE_SUPPLY_TRANSFER%rowtype;j json_object_t:=json_object_t();codes json_array_t:=json_array_t();site RRL_TRADE_SITE%rowtype;
 begin
  site:=lock_site(p_ware,p_actor,'tradecase_import',p_source);
  begin select*into t from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware and SOURCE_ID=p_source and TRANSFER_ID=p_transfer;
  exception when no_data_found then fail('SUPPLY_TRANSFER_NOT_FOUND');end;
  require_owner(p_actor,p_ware,t.HEADER_JSON,1);
  if t.STATUS not in('COMPLETE','DELIVERED')then fail('SUPPLY_TRANSFER_NOT_COMPLETE');end if;
  for p in(select CODES_JSON from RRL_TRADE_SUPPLY_PART where WARE_ID=p_ware and SOURCE_ID=p_source and TRANSFER_ID=p_transfer order by PART_NO)loop
   declare a json_array_t:=json_array_t.parse(p.CODES_JSON);begin for i in 0..a.get_size-1 loop codes.append(a.get(i));end loop;end;
  end loop;
  j.put('state',json_object_t.parse(state(p_ware,p_source,p_transfer,false)));j.put('header',json_object_t.parse(t.HEADER_JSON));
  j.put('codes',codes);j.put('end_occurred_at',t.END_OCCURRED_AT);
  p_result:=j.to_clob;
 end;

 procedure mark_delivered(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_json);t RRL_TRADE_SUPPLY_TRANSFER%rowtype;site RRL_TRADE_SITE%rowtype;
  src varchar2(100):=j.get_string('source_id');tr varchar2(100):=j.get_string('transfer_id');ev varchar2(100):=j.get_string('event_id');
  outcome varchar2(20):=j.get_string('outcome');rsn varchar2(200):=substr(j.get_string('reason'),1,200);res clob:=j.get_object('result').to_clob;
 begin
  site:=lock_site(p_ware,p_actor,'tradecase_import',src);
  select*into t from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware and SOURCE_ID=src and TRANSFER_ID=tr for update;
  require_owner(p_actor,p_ware,t.HEADER_JSON,1);
  if t.STATUS in('DELIVERED','DELIVERY_REJECTED')then
   if t.DELIVERED_EVENT_ID<>ev then fail('SUPPLY_DELIVERY_CONFLICT');end if;
   p_result:=state(p_ware,src,tr,true);return;
  end if;
  if t.STATUS<>'COMPLETE'or outcome not in('DELIVERED','DELIVERY_REJECTED')then fail('SUPPLY_TRANSFER_NOT_COMPLETE');end if;
  update RRL_TRADE_SUPPLY_TRANSFER set STATUS=outcome,STATUS_REASON=rsn,DELIVERED_EVENT_ID=ev,
   DELIVERY_RESULT=res,UPDATED_AT=systimestamp where WARE_ID=p_ware and SOURCE_ID=src and TRANSFER_ID=tr;
  p_result:=state(p_ware,src,tr,false);
 exception when no_data_found then fail('SUPPLY_TRANSFER_NOT_FOUND');
 end;

 procedure transfers(p_ware number,p_actor nvarchar2,p_limit number,p_result out clob)is
  a json_array_t:=json_array_t();r json_object_t:=json_object_t();n number:=0;
 begin
  RRL_ACCESS_API.assert_allowed(p_actor,'tradecase_view','WAREHOUSE',to_char(p_ware,'TM9'));
  if p_limit is null or p_limit<1 or p_limit>100 then fail('SUPPLY_TRANSFER_LIMIT');end if;
  -- Hidden owners are filtered before the bound: they are neither listed nor counted.
  for x in(select SOURCE_ID,TRANSFER_ID from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=p_ware
    and RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,json_value(HEADER_JSON,'$.owner_id'),0)=1
    order by case when STATUS in('OPEN','MISMATCH','COMPLETE')then 0 else 1 end,UPDATED_AT desc fetch first 101 rows only)loop
   n:=n+1;if n>p_limit then r.put('has_more',true);exit;end if;
   a.append(json_object_t.parse(state(p_ware,x.SOURCE_ID,x.TRANSFER_ID,false)));
  end loop;
  r.put('warehouse_id',p_ware);r.put('items',a);if not r.has('has_more')then r.put('has_more',false);end if;
  p_result:=r.to_clob;
 end;
end;
/
