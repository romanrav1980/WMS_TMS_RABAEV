 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);kind varchar2(80):=d.get_string('command_type');op varchar2(100):=d.get_string('operation_id');
 v json_object_t;fresh json_object_t;plan clob;j json_object_t:=json_object_t();
 v_owner number;v_type number;v_condition varchar2(10);v_from raw(32);v_to raw(32);v_to_kind varchar2(12);v_to_id varchar2(255);v_from_kind varchar2(12);v_from_id varchar2(255);
 v_qty number;v_before number;v_after number;v_version number;v_reason varchar2(2000);v_ref varchar2(255);v_offer varchar2(100);v_offered number;v_tt number;v_vehicle number;v_vehicle_num varchar2(50);v_store varchar2(255);n number;
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
 if kind!='TARE_COUNT' then
  v_tt:=v.get_number('task_id');v_vehicle:=v.get_number('vehicle_id');
  select ID into n from RRL_TRANSPORT_TASK where ID=v_tt for update;
  select ID into n from RRL_TR_VEHICLE where ID=v_vehicle for update;
 end if;
 for row_record in(select BALANCE_KEY from RRL_TARE_BALANCE where BALANCE_KEY in(hextoraw(v.get_string('from_key')),hextoraw(v.get_string('to_key')))order by BALANCE_KEY for update)loop null;end loop;
 describe_command(p_request,p_actor,fresh);
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: tare context or quantity');end if;
 v_owner:=v.get_number('owner_ware_id');v_type:=v.get_number('pallet_type_id');v_condition:=v.get_string('condition');
 v_from:=hextoraw(v.get_string('from_key'));v_to:=hextoraw(v.get_string('to_key'));v_to_kind:=v.get_string('to_kind');v_to_id:=v.get_string('to_id');v_from_kind:=v.get_string('from_kind');v_from_id:=v.get_string('from_id');
 v_qty:=integer_qty(v.get_string('quantity'),kind='TARE_COUNT');v_before:=to_number(v.get_string('to_quantity'));v_version:=v.get_number('to_version');
 if kind='TARE_OFFER' then
  v_vehicle_num:=v.get_string('vehicle_number');v_store:=v.get_string('store_address');
  insert into RRL_TARE_OFFER(OPERATION_ID,FROM_BALANCE_KEY,TO_BALANCE_KEY,TT_ID,VEHICLE_ID,VEHICLE_NUMBER,STORE_ADDR,OWNER_WARE_ID,PALLET_TYPE_ID,CONDITION_CODE,FROM_KIND,FROM_ID,TO_KIND,TO_ID,QUANTITY,OFFERED_BY)
  values(op,v_from,v_to,v_tt,v_vehicle,v_vehicle_num,v_store,v_owner,v_type,v_condition,v_from_kind,v_from_id,v_to_kind,v_to_id,v_qty,p_actor);
  j.put('status','WAITING_OTHER_PARTICIPANT');j.put('tare_balance_changed',false);
 else
  if kind='TARE_ACCEPT' then
   v_offer:=v.get_string('offer_operation_id');v_offered:=to_number(v.get_string('offered_quantity'));
   insert into RRL_TARE_ACCEPT(OPERATION_ID,OFFER_OPERATION_ID,ACCEPTED_QTY,SHORT_QTY,ACCEPTED_BY)values(op,v_offer,v_qty,v_offered-v_qty,p_actor);
   update RRL_TARE_BALANCE set QUANTITY=QUANTITY-v_qty,BALANCE_VERSION=BALANCE_VERSION+1,LAST_OPERATION_ID=op,UPDATED_AT=systimestamp
    where BALANCE_KEY=v_from and QUANTITY>=v_qty;
   if sql%rowcount!=1 then raise_application_error(-20886,'TARE_SOURCE_QUANTITY_UNAVAILABLE');end if;
   v_after:=v_before+v_qty;
  else v_after:=v_qty;v_reason:=v.get_string('reason');v_ref:=v.get_string('decision_reference');end if;
  merge into RRL_TARE_BALANCE b using(select v_to BALANCE_KEY from dual)s on(b.BALANCE_KEY=s.BALANCE_KEY)
  when matched then update set QUANTITY=v_after,BALANCE_VERSION=BALANCE_VERSION+1,LAST_OPERATION_ID=op,UPDATED_AT=systimestamp
  when not matched then insert(BALANCE_KEY,OWNER_WARE_ID,PALLET_TYPE_ID,CONDITION_CODE,CUSTODIAN_KIND,CUSTODIAN_ID,QUANTITY,BALANCE_VERSION,LAST_OPERATION_ID)
  values(v_to,v_owner,v_type,v_condition,v_to_kind,v_to_id,v_after,1,op);
  insert into RRL_TARE_JOURNAL(OPERATION_ID,ACTION_KIND,FROM_BALANCE_KEY,TO_BALANCE_KEY,QUANTITY,BEFORE_QTY,AFTER_QTY,REASON_TEXT,DECISION_REFERENCE,ACTOR)
  values(op,case when kind='TARE_COUNT' then 'COUNT' else 'TRANSFER' end,v_from,v_to,case when kind='TARE_COUNT' then v_after-v_before else v_qty end,v_before,v_after,v_reason,v_ref,p_actor);
  j.put('status','POSTED');j.put('tare_balance_changed',true);j.put('destination_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_after));
  if kind='TARE_ACCEPT' then j.put('offer_operation_id',v_offer);j.put('short_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_offered-v_qty));end if;
 end if;
 j.put('operation_id',op);j.put('quantity',v.get_string('quantity'));j.put('owner_ware_id',v_owner);j.put('pallet_type_id',v_type);j.put('condition',v_condition);
 j.put('goods_stock_changed',false);p_result:=j.to_clob;
 end;
end;
/
