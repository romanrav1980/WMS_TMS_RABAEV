create or replace package body RRL_TT_PLACE_REMOVAL_API as
 procedure fail(p_code varchar2) is begin raise_application_error(-20886,p_code);end;
 function source_hash(p_trip number,p_st varchar2) return varchar2 is s clob;n number;
 begin
  select count(*)into n from(select 1 from RRL_SBORKA_PALLETS where ST_NUMBER=p_st and rownum<=1001);
  if n>1000 then fail('ST_ASSIGNMENT_BATCH_BOUND');end if;
  dbms_lob.createtemporary(s,true);
  for t in(select ID,nvl(CONDITION,'-')C,nvl(DELETED,0)D,nvl(PAY_ORDER_ID,0)B,nvl(TRANSPORT,'-')V from RRL_TRANSPORT_TASK where ID=p_trip)loop
   dbms_lob.append(s,'T|'||t.ID||'|'||t.C||'|'||t.D||'|'||t.B||'|'||t.V||chr(10));
  end loop;
  for m in(select sp.ID,nvl(sp.TRANSTASK_ID,0)TT,nvl(sp.CONDITION,0)C,
   (select count(*) from RRL_TT_HU_LOAD_ST ls where ls.SBORKA_PALLET_ID=sp.ID and ls.ACTIVE_FLAG=1)L
   from RRL_SBORKA_PALLETS sp where sp.ST_NUMBER=p_st order by sp.ID)loop
   dbms_lob.append(s,'M|'||m.ID||'|'||m.TT||'|'||m.C||'|'||m.L||chr(10));
  end loop;
  return rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256));
 end;
 function replay(p_op varchar2,p_actor varchar2,p_hash varchar2,p_result out clob) return boolean is old RRL_TT_PLACE_REMOVAL_CMD%rowtype;
 begin
  select*into old from RRL_TT_PLACE_REMOVAL_CMD where OPERATION_ID=p_op;
  if old.ACTOR<>p_actor or old.REQUEST_HASH<>p_hash then fail('OPERATION_CONFLICT');end if;
  p_result:=old.RESULT_JSON;return true;  -- the exact stored reply, unchanged
 exception when no_data_found then return false;
 end;
 procedure remove(p_request clob,p_actor varchar2,p_result out clob) is
  j json_object_t:=json_object_t.parse(p_request);ids json_array_t;removed json_array_t:=json_array_t();r json_object_t;
  op varchar2(100):=j.get_string('operation_id');v_trip number:=j.get_number('trip_id');v_st varchar2(200):=j.get_string('st_number');
  v_expected varchar2(64):=j.get_string('expected_source_hash');v_hash varchar2(64);v_min number;v_max number;n number;v_count number;v_id number;answer varchar2(1024);
  task_state varchar2(100);deleted_flag number;bill number;
 begin
  if op is null or v_trip is null or v_trip<=0 or v_st is null or v_expected is null or not j.has('member_ids') then fail('PLACE_REMOVAL_INPUT_INVALID');end if;
  ids:=j.get_array('member_ids');
  if ids.get_size<1 or ids.get_size>200 then fail('PLACE_REMOVAL_BATCH_BOUND');end if;
  v_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  select count(*),count(WARE_ID),min(WARE_ID),max(WARE_ID)into n,v_count,v_min,v_max from RRL_SBORKA_PALLETS where ST_NUMBER=v_st;
  if n=0 then fail('ST_ASSIGNMENT_NOT_FOUND');end if;
  if v_count<>n then fail('ST_WAREHOUSE_REQUIRED');end if;  -- min/max ignore NULL: a place without a warehouse is refused explicitly
  if v_min<>v_max then fail('ST_WAREHOUSE_AMBIGUOUS');end if;
  -- Current rights before any stored reply, under the shared access-revision lock (as the other native commands).
  lock table RRL_ACCESS_REV in share mode wait 5;
  if RRL_ACCESS_API.allowed(p_actor,'transport_dispatch_edit','WAREHOUSE',to_char(v_min,'TM9'))<>1 then raise_application_error(-20882,'ACCESS_DENIED');end if;
  for o in(select distinct a.OWNER_ID from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID in(select f.PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT f
     where f.LEGACY_SBORKA_PALLET_ID in(select x.ID from json_table(p_request,'$.member_ids[*]' columns(ID number path '$'))x)
    union select ct.SSCC from RRL_CASE_PICK_TASK ct
     where ct.LEGACY_SBORKA_PALLET_ID in(select x.ID from json_table(p_request,'$.member_ids[*]' columns(ID number path '$'))x)))loop
   if RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,v_min,o.OWNER_ID,1)<>1 then raise_application_error(-20882,'TRADE_OWNER_ACCESS_DENIED');end if;
  end loop;
  if replay(op,p_actor,v_hash,p_result) then return;end if;
  -- The trip row first (the writer's TT -> member order); a competing command waits here and then sees the changed snapshot.
  select CONDITION,DELETED,PAY_ORDER_ID into task_state,deleted_flag,bill from RRL_TRANSPORT_TASK where ID=v_trip for update;
  -- The same operation may have been completed by a concurrent request while this one waited: the stored reply, not a new refusal.
  if replay(op,p_actor,v_hash,p_result) then return;end if;
  if nvl(deleted_flag,0)<>0 or task_state='Отгружен' or nvl(bill,0)>0 then fail('TRIP_MEMBERSHIP_CHANGE_FORBIDDEN');end if;
  if source_hash(v_trip,v_st)<>v_expected then fail('TRIP_MEMBERSHIP_SNAPSHOT_CHANGED');end if;
  select count(*)into n from(select x.ID from json_table(p_request,'$.member_ids[*]' columns(ID number path '$'))x group by x.ID having count(*)>1);
  if n>0 then fail('PLACE_REMOVAL_DUPLICATE_MEMBER');end if;
  for i in 0..ids.get_size-1 loop
   v_id:=ids.get_number(i);
   select count(*)into n from RRL_SBORKA_PALLETS where ID=v_id and ST_NUMBER=v_st and TRANSTASK_ID=v_trip;
   if n<>1 then fail('TRIP_MEMBER_NOT_ON_TRIP');end if;
   answer:=RRL_TT_ADD_PALL(0,v_st,v_id);
   removed.append(v_id);
  end loop;
  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=v_st and TRANSTASK_ID=v_trip;
  r:=json_object_t();r.put('operation_id',op);r.put('trip_id',v_trip);r.put('st_number',v_st);r.put('removed',removed);
  r.put('on_trip_after',n);r.put('stock_changed',false);r.put('source_hash_after',source_hash(v_trip,v_st));p_result:=r.to_clob;
  begin
   insert into RRL_TT_PLACE_REMOVAL_CMD(OPERATION_ID,ACTOR,REQUEST_HASH,TRIP_ID,ST_NUMBER,RESULT_JSON)values(op,p_actor,v_hash,v_trip,v_st,p_result);
  exception when dup_val_on_index then fail('OPERATION_CONFLICT');  -- the same operation on another trip: refused, the whole removal rolls back
  end;
 end;
end;
/
