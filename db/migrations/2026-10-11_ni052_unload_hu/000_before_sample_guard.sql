create or replace trigger RRL_QC_SAMPLE_GUARD
 before insert or update of QC_SAMPLE_BUCKET,QC_SAMPLE_REQUIRED,QC_RESCAN_REQUIRED on RRL_SBORKA_PALLETS for each row
declare v_op varchar2(100);v_kind varchar2(80);v_request clob;v_metadata json_object_t;
begin
 if inserting then
  if nvl(:new.QC_SAMPLE_REQUIRED,0)!=0 or nvl(:new.QC_RESCAN_REQUIRED,0)!=0 then raise_application_error(-20863,'QUALITY_SAMPLING_FLAGS_NOT_CLIENT_INPUT');end if;
  :new.QC_SAMPLE_BUCKET:=trunc(dbms_random.value(0,10000));return;
 end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'QUALITY_SAMPLING_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,CANONICAL_REQUEST into v_kind,v_request from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind='UNLOAD_SHIPMENT'then
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(:new.ID)));
  declare wire clob;state_name varchar2(20);sid number;begin
   select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
   sid:=json_object_t.parse(wire).get_object('domain').get_number('shipment_id');
   if state_name!='IN_FLIGHT'or sid!=:new.ID or nvl(:new.QC_SAMPLE_BUCKET,-1)!=nvl(:old.QC_SAMPLE_BUCKET,-1)or nvl(:new.QC_SAMPLE_REQUIRED,0)!=nvl(:old.QC_SAMPLE_REQUIRED,0)or :new.QC_RESCAN_REQUIRED!=1 then raise_application_error(-20863,'UNLOAD_RESCAN_ONLY_REQUIRED');end if;
  end;return;
 end if;
 if v_kind!='OUTGOING_PALLET_CHECK' then raise_application_error(-20863,'QUALITY_SAMPLING_COMMAND_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(:new.ID)));
 if :old.QC_SAMPLE_BUCKET is not null and nvl(:new.QC_SAMPLE_BUCKET,-1)!=:old.QC_SAMPLE_BUCKET then raise_application_error(-20863,'QUALITY_SAMPLE_BUCKET_IMMUTABLE');end if;
 if :old.QC_SAMPLE_REQUIRED=1 and :new.QC_SAMPLE_REQUIRED!=1 then raise_application_error(-20863,'QUALITY_SAMPLE_ASSIGNMENT_STICKY');end if;
 if :old.QC_RESCAN_REQUIRED=1 and :new.QC_RESCAN_REQUIRED=0 then
  v_metadata:=json_object_t.parse(v_request).get_object('metadata');
  if v_metadata.get_string('quality_kind')!='SCAN' or nvl(v_metadata.get_number('error_count'),-1)!=0 then raise_application_error(-20863,'QUALITY_FULL_RESCAN_REQUIRED');end if;
 end if;
end;
/
