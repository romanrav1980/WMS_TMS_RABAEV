create or replace package RRL_STOCK_COMPOSITION_CORE authid definer accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot_before(p_resources clob) return clob;
 procedure finish_changes(p_before clob);
end;
/
create or replace package body RRL_STOCK_COMPOSITION_CORE as
 function snapshot_before(p_resources clob) return clob is
  a json_array_t:=json_array_t();x json_object_t;v_uid varchar2(200);v_version number;v_qty number;v_sig varchar2(64);v_count number;v_units number:=0;v_uids number:=0;
 begin
  for k in(select distinct KEY_HEX from json_table(p_resources,'$[*]' columns(RANK_NO number path '$.rank',KEY_HEX varchar2(2000) path '$.key_hex')) where RANK_NO=50 order by KEY_HEX) loop
   v_uids:=v_uids+1;if v_uids>20000 then raise_application_error(-20881,'STOCK_COMPOSITION_UID_BOUND_20000');end if;
   v_uid:=RRL_STOCK_INVARIANT_CORE.stock_uid(hextoraw(k.KEY_HEX));
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_PALLETS',v_uid));
   select nvl(max(STOCK_COMPOSITION_VERSION),0) into v_version from RRL_PALLETS where UID_PALLET=v_uid;
   select nvl(sum(REMAIN),0) into v_qty from RRL_REMAINS where UID_POLETA=v_uid;
   RRL_STOCK_HU_UNIT_SIGNATURE.describe_units(v_uid,null,v_sig,v_count);
   v_units:=v_units+v_count;if v_units>20000 then raise_application_error(-20881,'STOCK_COMPOSITION_UNIT_BOUND_20000');end if;
   x:=json_object_t();x.put('uid',v_uid);x.put('version',v_version);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));x.put('unit_signature',v_sig);a.append(x);
  end loop;
  return a.to_clob;
 end;
 procedure finish_changes(p_before clob) is
  a json_array_t:=json_array_t.parse(p_before);x json_object_t;v_uid varchar2(200);v_version number;v_qty number;v_sig varchar2(64);v_count number;v_units number:=0;changed json_array_t:=json_array_t();changes clob;row_no number;op varchar2(100);actor_name varchar2(50);event_payload clob;j json_object_t;
 begin
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);v_uid:=x.get_string('uid');v_version:=x.get_number('version');
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
   select nvl(sum(REMAIN),0) into v_qty from RRL_REMAINS where UID_POLETA=v_uid;
   RRL_STOCK_HU_UNIT_SIGNATURE.describe_units(v_uid,null,v_sig,v_count);
   v_units:=v_units+v_count;if v_units>20000 then raise_application_error(-20881,'STOCK_COMPOSITION_UNIT_BOUND_20000');end if;
   if RRL_STOCK_PLAN_HELPER.decimal_text(v_qty)!=x.get_string('quantity') or v_sig!=x.get_string('unit_signature') then
    RRL_STOCK_CTX_API.begin_effect('COMPOSITION',v_uid);
    update RRL_PALLETS set STOCK_COMPOSITION_VERSION=STOCK_COMPOSITION_VERSION+1 where UID_PALLET=v_uid and STOCK_COMPOSITION_VERSION=v_version;
    if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: stock composition epoch');end if;
    RRL_STOCK_CTX_API.end_effect;changed.append(v_uid);
   end if;
  end loop;
  if changed.get_size=0 then return;end if;changes:=changed.to_clob;
  -- Match QC/physical packing actual-row order. Every row was declared before locking.
  for st in(select ID from RRL_SBORKA_PALLETS where nvl(CONDITION,0)<2 and ID in(
   select LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(
    select CASE_PICK_TASK_ID from RRL_CASE_CARRIER_LOT where LOT_UID in(select U from json_table(changes,'$[*]' columns(U varchar2(200) path '$'))))
   union select LEGACY_SBORKA_PALLET_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_PALLET_UID in(select U from json_table(changes,'$[*]' columns(U varchar2(200) path '$')))) order by ID) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(st.ID)));
   select ID into row_no from RRL_SBORKA_PALLETS where ID=st.ID for update;
   update RRL_SBORKA_PALLETS set SCAN_CONTENT_SIGNATURE=null,WEIGHT_CONTENT_SIGNATURE=null,
    SCAN_MARK_PROVED=0,SCAN_PHYSICAL_UNIT_COUNT=0,SCAN_ITEM_PROVED=0 where ID=st.ID;
  end loop;
  op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');select ACTOR into actor_name from RRL_STOCK_OPERATION where OPERATION_ID=op;
  for ct in(select CASE_PICK_TASK_ID,STATUS from RRL_CASE_PICK_TASK where STATUS in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP') and CASE_PICK_TASK_ID in(
   select CASE_PICK_TASK_ID from RRL_CASE_CARRIER_LOT where LOT_UID in(select U from json_table(changes,'$[*]' columns(U varchar2(200) path '$')))) order by CASE_PICK_TASK_ID) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(ct.CASE_PICK_TASK_ID)));
   select CASE_PICK_TASK_ID into row_no from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID for update;
   update RRL_CASE_PICK_TASK set STATUS='WAIT_CONTROL',CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=actor_name where CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID;
   j:=json_object_t();j.put('operation_id',op);j.put('reason','STOCK_COMPOSITION_CHANGED');j.put('previous_status',ct.STATUS);event_payload:=j.to_clob;
   insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY)
    values(RRL_CASE_PICK_EVENT_SQ.nextval,ct.CASE_PICK_TASK_ID,'CONTROL_REVOKED',event_payload,actor_name);
  end loop;
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
end;
/
