create or replace package body RRL_TRADE_TRANSPORT_CORE as
 procedure fail(p_code varchar2)is begin raise_application_error(-20886,p_code);end;
 function signature(p_trip number)return varchar2 is d json_object_t:=json_object_t();a json_array_t:=json_array_t();x json_object_t;plate varchar2(100);dock_name varchar2(100);driver_no number;v_hash varchar2(64);n number:=0;
 begin
  select TRANSPORT,DOCK,VODITEL_ID into plate,dock_name,driver_no from RRL_TRANSPORT_TASK where ID=p_trip;
  d.put('task',p_trip);d.put('vehicle',plate);d.put('dock',dock_name);d.put('driver',driver_no);
  for ld in(select LOAD_OPERATION_ID,CONTENT_VERSION,ROOT_UID,GROSS_WEIGHT_KG,BOUNDING_VOLUME_M3 from RRL_TT_HU_LOAD_FACT where TT_ID=p_trip and STATUS in('LOADED','DEPARTED')order by LOAD_OPERATION_ID)loop
   n:=n+1;if n>200 then fail('TRADE_MANIFEST_BOUND_200');end if;
   -- Applied LOAD IDs identify immutable frozen compositions; re-load/reconcile uses a new operation.
   x:=json_object_t();x.put('load',ld.LOAD_OPERATION_ID);x.put('version',ld.CONTENT_VERSION);x.put('root',ld.ROOT_UID);x.put('gross',ld.GROSS_WEIGHT_KG);x.put('volume',ld.BOUNDING_VOLUME_M3);a.append(x);
  end loop;d.put('loads',a);a:=json_array_t();
  n:=0;for st in(select ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip order by ID)loop n:=n+1;if n>200 then fail('TRADE_MANIFEST_MEMBER_BOUND_200');end if;a.append(st.ID);end loop;d.put('members',a);
  return rawtohex(sys.dbms_crypto.hash(d.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure validate_members(p_ware number,native_id number,wire clob)is
  native_row number;article varchar2(160);input_unit varchar2(20);num number;den number;actual_qty number;expected_qty number;n number;
 begin
  select count(*)into n from RRL_SBORKA_PALLETS sp where sp.TRANSTASK_ID=native_id and sp.WARE_ID=p_ware and not exists(
   select 1 from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_TRADE_ORDER_LINK tl on tl.CUSTOMER_ORDER_ID=f.CUSTOMER_ORDER_ID where f.LEGACY_SBORKA_PALLET_ID=sp.ID and tl.WARE_ID=p_ware);
  if n>0 then fail('TRADE_TRIP_UNBOUND_NATIVE_MEMBER');end if;
  for assignment in(select ORDER_ID,LINE_ID,QUANTITY from json_table(wire,'$.orders[*]'columns(ORDER_ID varchar2(100)path'$.order_id',LINE_ID varchar2(100)path'$.line_id',QUANTITY number path'$.quantity')))loop
   select count(*)into n from RRL_TRADE_ORDER_LINK tl join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=tl.CUSTOMER_ORDER_ID
    join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.CUSTOMER_ORDER_ID=tl.CUSTOMER_ORDER_ID join RRL_SBORKA_PALLETS sp on sp.ID=f.LEGACY_SBORKA_PALLET_ID and sp.TRANSTASK_ID=native_id
    where tl.WARE_ID=p_ware and tl.EXTERNAL_ID=assignment.ORDER_ID and ol.EXTERNAL_LINE_ID=assignment.LINE_ID;
   if n=0 then fail('TRADE_TRIP_NATIVE_MEMBERSHIP_REQUIRED');end if;
  end loop;
  -- Canonical trip quantities use their original order unit; compare exact base quantities.
  for assignment in(select ORDER_ID,LINE_ID,QUANTITY from json_table(wire,'$.orders[*]'columns(ORDER_ID varchar2(100)path'$.order_id',LINE_ID varchar2(100)path'$.line_id',QUANTITY number path'$.quantity')))loop
   select ol.CUSTOMER_ORDER_ROW_ID,cr.ARTICUL,cr.UNIT_CODE into native_row,article,input_unit from RRL_TRADE_ORDER_LINK tl
    join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=tl.CUSTOMER_ORDER_ID join RRL_CUSTOMER_ORDER_ROW cr on cr.CUSTOMER_ORDER_ROW_ID=ol.CUSTOMER_ORDER_ROW_ID
    join RRL_TRADE_DOCUMENT od on od.WARE_ID=tl.WARE_ID and od.ENTITY_TYPE='ORDER'and od.EXTERNAL_ID=tl.EXTERNAL_ID and od.VERSION_NO=tl.DOCUMENT_VERSION and od.STATUS='ACCEPTED'
    where tl.WARE_ID=p_ware and tl.EXTERNAL_ID=assignment.ORDER_ID and ol.EXTERNAL_LINE_ID=assignment.LINE_ID;
   select case when input_unit='EA'then 1 when input_unit='BOX'then json_value(sd.BODY_JSON,'$.units_per_box'returning number)end,1 into num,den
    from RRL_TRADE_ORDER_LINE ol join RRL_TRADE_DOCUMENT sd on sd.WARE_ID=p_ware and sd.ENTITY_TYPE='SKU'and sd.EXTERNAL_ID=ol.SKU_ID and sd.VERSION_NO=ol.SKU_VERSION and sd.STATUS='ACCEPTED'where ol.CUSTOMER_ORDER_ROW_ID=native_row;
   if num is null or num<=0 then fail('TRADE_TRIP_BOUND_PACKAGING_REQUIRED');end if;
   expected_qty:=assignment.QUANTITY*num/den;
   select nvl(sum(QTY),0)into actual_qty from(
    select cl.PICKED_QTY QTY from RRL_CASE_PICK_LINE cl join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=cl.PICK_PLAN_LINE_ID
     join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=cl.CASE_PICK_TASK_ID join RRL_SBORKA_PALLETS sp on sp.ID=ct.LEGACY_SBORKA_PALLET_ID
     where pl.CUSTOMER_ORDER_ROW_ID=native_row and sp.TRANSTASK_ID=native_id
    union all select pt.QTY from RRL_PICK_TASK pt join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
     join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_PALLET_UID=pt.PALLET_UID join RRL_SBORKA_PALLETS sp on sp.ID=f.LEGACY_SBORKA_PALLET_ID
     where pl.CUSTOMER_ORDER_ROW_ID=native_row and pt.TASK_TYPE='FULL_PALLET'and pt.STATUS='DONE'and sp.TRANSTASK_ID=native_id);
   if actual_qty<>expected_qty or expected_qty<=0 then fail('TRADE_TRIP_PHYSICAL_QUANTITY_MISMATCH');end if;
  end loop;
  for actual_line in(select distinct tl.EXTERNAL_ID,ol.EXTERNAL_LINE_ID from RRL_CASE_PICK_TASK ct join RRL_CASE_PICK_LINE cl on cl.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID
   join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=cl.PICK_PLAN_LINE_ID join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID
   join RRL_TRADE_ORDER_LINK tl on tl.CUSTOMER_ORDER_ID=ol.CUSTOMER_ORDER_ID join RRL_SBORKA_PALLETS sp on sp.ID=ct.LEGACY_SBORKA_PALLET_ID
   where sp.TRANSTASK_ID=native_id and sp.WARE_ID=p_ware and cl.PICKED_QTY>0
   union select distinct tl.EXTERNAL_ID,ol.EXTERNAL_LINE_ID from RRL_PICK_TASK pt join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
    join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID join RRL_TRADE_ORDER_LINK tl on tl.CUSTOMER_ORDER_ID=ol.CUSTOMER_ORDER_ID
    join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_PALLET_UID=pt.PALLET_UID join RRL_SBORKA_PALLETS sp on sp.ID=f.LEGACY_SBORKA_PALLET_ID
    where sp.TRANSTASK_ID=native_id and sp.WARE_ID=p_ware and pt.TASK_TYPE='FULL_PALLET'and pt.STATUS='DONE'and pt.QTY>0)loop
   select count(*)into n from json_table(wire,'$.orders[*]'columns(ORDER_ID varchar2(100)path'$.order_id',LINE_ID varchar2(100)path'$.line_id'))x where x.ORDER_ID=actual_line.EXTERNAL_ID and x.LINE_ID=actual_line.EXTERNAL_LINE_ID;
   if n<>1 then fail('TRADE_TRIP_UNLISTED_PHYSICAL_ORDER');end if;
  end loop;
 end;
 procedure current_plan(p_ware number,l RRL_TRADE_TRIP_LINK%rowtype)is n number;wire clob;
 begin
  select count(*)into n from RRL_TRADE_DOCUMENT d join RRL_TRANSPORT_TASK tt on tt.ID=l.NATIVE_TASK_ID where d.WARE_ID=p_ware and d.ENTITY_TYPE='TRIP'and d.EXTERNAL_ID=l.TRIP_ID and d.VERSION_NO=l.TRIP_VERSION and d.STATUS='ACCEPTED'and nvl(json_value(d.BODY_JSON,'$.cancelled'),'false')='false'and tt.TRANSPORT=json_value(d.BODY_JSON,'$.vehicle_id');
  if n<>1 then fail('TRADE_TRIP_BINDING_STALE');end if;
  select BODY_JSON into wire from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='TRIP'and EXTERNAL_ID=l.TRIP_ID;validate_members(p_ware,l.NATIVE_TASK_ID,wire);
  select count(*)into n from RRL_TRADE_DOCUMENT tr,json_table(tr.BODY_JSON,'$.orders[*]'columns(ORDER_ID varchar2(100)path'$.order_id',LINE_ID varchar2(100)path'$.line_id'))x
   where tr.WARE_ID=p_ware and tr.ENTITY_TYPE='TRIP'and tr.EXTERNAL_ID=l.TRIP_ID and not exists(
    select 1 from RRL_TRADE_ORDER_LINK tl join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=tl.CUSTOMER_ORDER_ID
     join RRL_TRADE_DOCUMENT od on od.WARE_ID=tl.WARE_ID and od.ENTITY_TYPE='ORDER'and od.EXTERNAL_ID=tl.EXTERNAL_ID and od.VERSION_NO=tl.DOCUMENT_VERSION and od.STATUS='ACCEPTED'and nvl(json_value(od.BODY_JSON,'$.cancelled'),'false')='false'
     join RRL_TRADE_DOCUMENT rd on rd.WARE_ID=tl.WARE_ID and rd.ENTITY_TYPE='RECIPIENT'and rd.EXTERNAL_ID=tl.RECIPIENT_ID and rd.VERSION_NO=tl.RECIPIENT_VERSION and rd.STATUS='ACCEPTED'and json_value(rd.BODY_JSON,'$.active')='true'
     join RRL_TRADE_DOCUMENT sd on sd.WARE_ID=tl.WARE_ID and sd.ENTITY_TYPE='SKU'and sd.EXTERNAL_ID=ol.SKU_ID and sd.VERSION_NO=ol.SKU_VERSION and sd.STATUS='ACCEPTED'and json_value(sd.BODY_JSON,'$.active')='true'
    where tl.WARE_ID=p_ware and tl.EXTERNAL_ID=x.ORDER_ID and ol.EXTERNAL_LINE_ID=x.LINE_ID);
  if n>0 then fail('TRADE_TRANSPORT_DEMAND_BINDING_STALE');end if;
 end;
 procedure bind_trip(p_ware number,p_actor varchar2,j json_object_t,r in out nocopy json_object_t)is
  id_value varchar2(100):=j.get_string('trip_id');native_id number:=j.get_number('native_task_id');expected number:=j.get_number('expected_binding_version');
  v_doc_version number;wire clob;d json_object_t;old RRL_TRADE_TRIP_LINK%rowtype;plate varchar2(100);n number;hash_value varchar2(64):=j.get_string('business_hash');new_version number:=1;src varchar2(100);result_wire clob;native_row number;article varchar2(160);input_unit varchar2(20);num number;den number;actual_qty number;expected_qty number;
 begin
  if expected is null or expected<0 or expected<>trunc(expected)or native_id is null or native_id<=0 or j.get_number('expected_trip_version')is null then fail('TRADE_TRIP_BINDING_REQUEST_REQUIRED');end if;
  begin select *into old from RRL_TRADE_TRIP_LINK where WARE_ID=p_ware and TRIP_ID=id_value;
   if old.REQUEST_HASH=hash_value then r:=json_object_t.parse(old.RESULT_JSON);r.put('business_replayed',true);return;end if;
   if old.VERSION_NO<>expected then fail('TRADE_TRIP_BINDING_VERSION_CONFLICT');end if;new_version:=old.VERSION_NO+1;
  exception when no_data_found then if expected<>0 then fail('TRADE_TRIP_BINDING_VERSION_CONFLICT');end if;end;
  select BODY_JSON,VERSION_NO into wire,v_doc_version from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='TRIP'and EXTERNAL_ID=id_value and STATUS='ACCEPTED';d:=json_object_t.parse(wire);
  if v_doc_version<>j.get_number('expected_trip_version')or d.get_boolean('cancelled')then fail('TRADE_TRIP_VERSION_CONFLICT');end if;
  select TRANSPORT into plate from RRL_TRANSPORT_TASK where ID=native_id for update wait 5;
  if plate<>d.get_string('vehicle_id')or plate is null then fail('TRADE_TRIP_VEHICLE_MAPPING_REQUIRED');end if;
  select count(*)into n from RRL_TT_HU_LOAD_FACT where TT_ID=native_id and STATUS='DEPARTED';if n>0 then fail('TRADE_TRIP_ALREADY_DEPARTED');end if;
  validate_members(p_ware,native_id,wire);
  select SOURCE_ID into src from RRL_TRADE_SITE where WARE_ID=p_ware;
  r.put('trip_id',id_value);r.put('trip_version',v_doc_version);r.put('native_task_id',native_id);r.put('binding_version',new_version);r.put('document_ready',false);
  result_wire:=r.to_clob;
  merge into RRL_TRADE_TRIP_LINK t using(select p_ware WARE_ID,id_value TRIP_ID from dual)s on(t.WARE_ID=s.WARE_ID and t.TRIP_ID=s.TRIP_ID)
  when matched then update set t.TRIP_VERSION=v_doc_version,t.NATIVE_TASK_ID=native_id,t.VERSION_NO=new_version,t.SOURCE_ID=src,t.REQUEST_HASH=hash_value,t.RESULT_JSON=result_wire
  when not matched then insert(WARE_ID,TRIP_ID,TRIP_VERSION,NATIVE_TASK_ID,VERSION_NO,SOURCE_ID,REQUEST_HASH,RESULT_JSON)values(p_ware,id_value,v_doc_version,native_id,new_version,src,hash_value,result_wire);
 end;
 procedure confirm_document(p_ware number,p_actor varchar2,j json_object_t,r in out nocopy json_object_t)is
  id_value varchar2(100):=j.get_string('trip_id');event_value varchar2(100):=j.get_string('external_event_id');src varchar2(100):=j.get_string('source_id');
  v_doc_version number:=j.get_number('document_version');status_value varchar2(10):=j.get_string('document_status');docid varchar2(100):=j.get_string('external_document_id');
  v_signature varchar2(64):=j.get_string('manifest_signature');hash_value varchar2(64):=j.get_string('business_hash');reason_value varchar2(2000):=j.get_string('error_reason');
  l RRL_TRADE_TRIP_LINK%rowtype;old RRL_TRADE_TRIP_DOC_EVENT%rowtype;n number;wire clob;result_wire clob;outbox_id number;event_key varchar2(500);
 begin
  begin select *into old from RRL_TRADE_TRIP_DOC_EVENT where WARE_ID=p_ware and SOURCE_ID=src and EVENT_ID=event_value;
   if old.REQUEST_HASH<>hash_value then fail('TRADE_TRANSPORT_EVENT_CONFLICT');end if;r:=json_object_t.parse(old.RESULT_JSON);r.put('business_replayed',true);return;
  exception when no_data_found then null;end;
  select *into l from RRL_TRADE_TRIP_LINK where WARE_ID=p_ware and TRIP_ID=id_value for update wait 5;current_plan(p_ware,l);
  if src is null or j.get_number('expected_trip_version')is null or j.get_number('expected_binding_version')is null or src<>l.SOURCE_ID or l.TRIP_VERSION<>j.get_number('expected_trip_version')or l.VERSION_NO<>j.get_number('expected_binding_version')then fail('TRADE_TRANSPORT_SOURCE_VERSION_CONFLICT');end if;
  select nvl(max(DOCUMENT_VERSION),0)into n from RRL_TRADE_TRIP_DOC_EVENT where WARE_ID=p_ware and TRIP_ID=id_value;
  if v_doc_version is null or v_doc_version<>trunc(v_doc_version)or v_doc_version<=n then fail('TRADE_TRANSPORT_DOCUMENT_VERSION_CONFLICT');end if;
  if status_value not in('READY','ERROR','REVOKED')or status_value is null or(status_value='READY'and docid is null)or(status_value<>'READY'and reason_value is null)then fail('TRADE_TRANSPORT_RESULT_REQUIRED');end if;
  if v_signature is null or v_signature<>signature(l.NATIVE_TASK_ID)then fail('TRADE_TRANSPORT_MANIFEST_CHANGED');end if;
  if status_value='READY'then
   select count(*)into n from RRL_SBORKA_PALLETS sp where sp.TRANSTASK_ID=l.NATIVE_TASK_ID and not exists(select 1 from RRL_TT_HU_LOAD_ST s join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=s.LOAD_OPERATION_ID where s.SBORKA_PALLET_ID=sp.ID and f.TT_ID=l.NATIVE_TASK_ID and f.STATUS='LOADED');
   if n>0 then fail('TRADE_TRANSPORT_MANIFEST_INCOMPLETE');end if;
   select count(*)into n from RRL_TT_HU_LOAD_FACT where TT_ID=l.NATIVE_TASK_ID and STATUS='LOADED';if n=0 then fail('TRADE_TRANSPORT_MANIFEST_INCOMPLETE');end if;
  end if;
  r.put('trip_id',id_value);r.put('document_version',v_doc_version);r.put('document_status',status_value);r.put('external_document_id',docid);r.put('document_ready',status_value='READY');r.put('manifest_signature',v_signature);
  event_key:='TC:TD:'||p_ware||':'||src||':'||event_value;
  outbox_id:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_TRANSPORT_DOCUMENT_RESULT','TRADE_TRIP',id_value,event_key,r.to_clob,'TRADECASE_BUS',j.get_string('operation_id'));r.put('outbox_id',outbox_id);
  wire:=j.to_clob;result_wire:=r.to_clob;
  insert into RRL_TRADE_TRIP_DOC_EVENT(WARE_ID,SOURCE_ID,EVENT_ID,TRIP_ID,TRIP_VERSION,BINDING_VERSION,DOCUMENT_VERSION,DOCUMENT_STATUS,EXTERNAL_DOCUMENT_ID,MANIFEST_SIGNATURE,ERROR_REASON,REQUEST_HASH,REQUEST_JSON,RESULT_JSON)
   values(p_ware,src,event_value,id_value,l.TRIP_VERSION,l.VERSION_NO,v_doc_version,status_value,docid,v_signature,reason_value,hash_value,wire,result_wire);
 end;
 procedure read_state(p_ware number,p_actor varchar2,j json_object_t,p_result out clob)is
  l RRL_TRADE_TRIP_LINK%rowtype;d RRL_TRADE_TRIP_DOC_EVENT%rowtype;id_value varchar2(100):=j.get_string('trip_id');r json_object_t:=json_object_t();sig varchar2(64);n number;plan_current number:=1;loads json_array_t:=json_array_t();item json_object_t;
 begin
  select *into l from RRL_TRADE_TRIP_LINK where WARE_ID=p_ware and TRIP_ID=id_value;sig:=signature(l.NATIVE_TASK_ID);
  begin current_plan(p_ware,l);exception when others then if sqlcode in(-20886,100,-1403,-1422)then plan_current:=0;else raise;end if;end;
  r.put('basis_current',plan_current=1);
  r.put('trip_id',id_value);r.put('native_task_id',l.NATIVE_TASK_ID);r.put('trip_version',l.TRIP_VERSION);r.put('binding_version',l.VERSION_NO);r.put('manifest_signature',sig);r.put('document_ready',false);
  for ld in(select lf.LOAD_OPERATION_ID,lf.STATUS,lf.ROOT_UID,lf.CONTENT_VERSION,lf.DEPARTED_AT,lf.CUSTODY_RELEASED_AT,ct.SSCC
   from RRL_TT_HU_LOAD_FACT lf left join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=lf.ROOT_CASE_TASK_ID
   where lf.TT_ID=l.NATIVE_TASK_ID and lf.WARE_ID=p_ware order by lf.LOAD_OPERATION_ID fetch first 201 rows only)loop
   if loads.get_size>=200 then fail('TRADE_MANIFEST_BOUND_200');end if;
   item:=json_object_t();item.put('load_operation_id',ld.LOAD_OPERATION_ID);item.put('status',ld.STATUS);item.put('identifier',nvl(ld.SSCC,ld.ROOT_UID));item.put('content_version',ld.CONTENT_VERSION);
   item.put('departed_at',to_char(ld.DEPARTED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF3TZH:TZM'));item.put('custody_released',ld.CUSTODY_RELEASED_AT is not null);loads.append(item);
  end loop;r.put('loads',loads);
  begin
   select *into d from RRL_TRADE_TRIP_DOC_EVENT where WARE_ID=p_ware and TRIP_ID=id_value order by DOCUMENT_VERSION desc fetch first 1 rows only;
   r.put('document_version',d.DOCUMENT_VERSION);r.put('document_status',d.DOCUMENT_STATUS);r.put('external_document_id',d.EXTERNAL_DOCUMENT_ID);r.put('error_reason',d.ERROR_REASON);r.put('manifest_matched',d.MANIFEST_SIGNATURE=sig);
   select count(*)into n from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='TRIP'and EXTERNAL_ID=id_value and VERSION_NO=l.TRIP_VERSION and STATUS='ACCEPTED'and nvl(json_value(BODY_JSON,'$.cancelled'),'false')='false';
   r.put('document_ready',plan_current=1 and n=1 and d.DOCUMENT_STATUS='READY'and d.MANIFEST_SIGNATURE=sig and d.TRIP_VERSION=l.TRIP_VERSION and d.BINDING_VERSION=l.VERSION_NO);
  exception when no_data_found then r.put('document_status','MISSING');end;p_result:=r.to_clob;
 end;
 procedure assert_departure(p_trip number)is l RRL_TRADE_TRIP_LINK%rowtype;d RRL_TRADE_TRIP_DOC_EVENT%rowtype;n number;
 begin
  for w in(select distinct sp.WARE_ID from RRL_SBORKA_PALLETS sp join RRL_TRADE_SITE s on s.WARE_ID=sp.WARE_ID where sp.TRANSTASK_ID=p_trip)loop
   begin select *into l from RRL_TRADE_TRIP_LINK where WARE_ID=w.WARE_ID and NATIVE_TASK_ID=p_trip;exception when no_data_found then fail('TRADE_TRANSPORT_TRIP_BINDING_REQUIRED');end;
   current_plan(w.WARE_ID,l);
   begin select *into d from RRL_TRADE_TRIP_DOC_EVENT where WARE_ID=w.WARE_ID and TRIP_ID=l.TRIP_ID order by DOCUMENT_VERSION desc fetch first 1 rows only;exception when no_data_found then fail('TRADE_TRANSPORT_DOCUMENT_REQUIRED');end;
   if d.DOCUMENT_STATUS<>'READY'or d.TRIP_VERSION<>l.TRIP_VERSION or d.BINDING_VERSION<>l.VERSION_NO or d.MANIFEST_SIGNATURE<>signature(p_trip)then fail('TRADE_TRANSPORT_DOCUMENT_NOT_READY');end if;
  end loop;
 end;
end;
/
