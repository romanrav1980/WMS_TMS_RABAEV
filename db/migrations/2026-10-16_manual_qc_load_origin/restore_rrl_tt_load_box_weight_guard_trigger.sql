create or replace trigger RRL_TT_LOAD_BOX_WEIGHT_GUARD before insert or update or delete on RRL_TT_LOAD_BOX_WEIGHT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);wire clob;d json_object_t;a json_array_t;x json_object_t;n number:=0;
 function same(p_one varchar2,p_two varchar2)return boolean is begin if p_one is null then return p_two is null;end if;return p_two is not null and p_one=p_two;end;
begin
 if not inserting then raise_application_error(-20863,'LOAD_BOX_WEIGHT_IMMUTABLE');end if;
 if op is null or op!=:new.LOAD_OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'LOAD_BOX_WEIGHT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind not in('HU_SHIP','LOAD_SHIPMENT','RECONCILE_HU_LOAD') or v_state!='IN_FLIGHT' then raise_application_error(-20863,'LOAD_BOX_WEIGHT_ROOT_REQUIRED');end if;

 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
 d:=json_object_t.parse(wire).get_object('domain');a:=d.get_object('loading').get_array('physical_boxes');
 if a.get_size>200 then raise_application_error(-20863,'LOAD_BOX_ROOT_BOUND');end if;
 for i in 0..a.get_size-1 loop
  x:=treat(a.get(i)as json_object_t);
  if x.get_string('box_uid')=:new.BOX_UID then
   n:=n+1;
   if x.get_number('content_version')!=:new.BOX_CONTENT_VERSION or RRL_STOCK_MATH.quantity(x.get_string('gross_weight_kg'))!=:new.GROSS_WEIGHT_KG
    or not same(x.get_string('origin'),:new.MEASUREMENT_ORIGIN)or not same(x.get_string('measurement_ref'),:new.MEASUREMENT_REF)
    or not same(x.get_string('scan_box'),:new.SCAN_IDENTIFIER)or nvl(x.get_number('coverage_complete'),1)!=:new.COVERAGE_COMPLETE
    or nvl(x.get_number('case_task_id'),-1)!=nvl(:new.CASE_BOX_TASK_ID,-1)
    or not same(x.get_string('final_scale_capture'),:new.FINAL_SCALE_CAPTURE)or not same(x.get_string('warehouse_qc_operation'),:new.WAREHOUSE_QC_OPERATION)
    or not same(x.get_string('device_mode'),:new.DEVICE_MODE)or not same(x.get_string('composition_signature'),:new.COMPOSITION_SIGNATURE)
    or nvl(x.get_number('signature_version'),-1)!=nvl(:new.SIGNATURE_VERSION,-1)
    or nvl(x.get_number('measured_content_version'),-1)!=nvl(:new.MEASURED_CONTENT_VERSION,-1)
    then raise_application_error(-20863,'LOAD_BOX_ORIGINAL_FROZEN_PLAN_REQUIRED');end if;
   if :new.MEASUREMENT_ORIGIN='WAREHOUSE_SCALE_QC'then
    if RRL_STOCK_MATH.quantity(x.get_string('tare_weight_kg'))!=:new.TARE_WEIGHT_KG or RRL_STOCK_MATH.quantity(x.get_string('net_weight_kg'))!=:new.NET_WEIGHT_KG
     then raise_application_error(-20863,'LOAD_CASE_ORIGINAL_GROSS_TARE_NET_REQUIRED');end if;
   end if;
  end if;
 end loop;
 if n!=1 then raise_application_error(-20863,'LOAD_BOX_ONE_FROZEN_PLAN_ROW_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_LOAD_BOX_WEIGHT',op||':'||:new.BOX_UID));
end;
/
