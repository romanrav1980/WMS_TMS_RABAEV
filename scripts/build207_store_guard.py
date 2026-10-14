from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_case_mass");out={}
s=(f/"000_before_guard.sql").read_text(encoding="utf-8")
s=s.replace("v_state varchar2(20);","v_state varchar2(20);wire clob;d json_object_t;a json_array_t;x json_object_t;n number:=0;\n function same(p_one varchar2,p_two varchar2)return boolean is begin if p_one is null then return p_two is null;end if;return p_two is not null and p_one=p_two;end;")
needle=" RRL_STOCK_LOCK_API.assert_held(20"
pos=s.index(needle)
s=s[:pos]+"""
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
"""+s[pos:]
out[str(f/"007_guard.sql")]=s
s=(f/"000_before_store.sql").read_text(encoding="utf-8")
needle="BOX_UID,BOX_CONTENT_VERSION,GROSS_WEIGHT_KG,MEASUREMENT_ORIGIN,MEASUREMENT_REF,RECORDED_BY from RRL_TT_LOAD_BOX_WEIGHT"
assert s.count(needle)==1
s=s.replace(needle,"BOX_UID,BOX_CONTENT_VERSION,GROSS_WEIGHT_KG,MEASUREMENT_ORIGIN,MEASUREMENT_REF,RECORDED_BY,SCAN_IDENTIFIER,CASE_BOX_TASK_ID,FINAL_SCALE_CAPTURE,WAREHOUSE_QC_OPERATION,TARE_WEIGHT_KG,NET_WEIGHT_KG,DEVICE_MODE,COMPOSITION_SIGNATURE,SIGNATURE_VERSION,MEASURED_CONTENT_VERSION,COVERAGE_COMPLETE from RRL_TT_LOAD_BOX_WEIGHT")
needle="box_json.put('recorded_by',box.RECORDED_BY);physical_boxes.append(box_json);"
assert s.count(needle)==1
s=s.replace(needle,"""box_json.put('recorded_by',box.RECORDED_BY);box_json.put('scan_identifier',box.SCAN_IDENTIFIER);box_json.put('coverage_complete',box.COVERAGE_COMPLETE=1);
   if box.CASE_BOX_TASK_ID is not null then
    box_json.put('case_task_id',box.CASE_BOX_TASK_ID);box_json.put('sscc',box.SCAN_IDENTIFIER);box_json.put('final_scale_capture',box.FINAL_SCALE_CAPTURE);box_json.put('warehouse_qc_operation',box.WAREHOUSE_QC_OPERATION);
    box_json.put('tare_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(box.TARE_WEIGHT_KG));box_json.put('net_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(box.NET_WEIGHT_KG));
    box_json.put('device_mode',box.DEVICE_MODE);box_json.put('composition_signature',box.COMPOSITION_SIGNATURE);box_json.put('signature_version',box.SIGNATURE_VERSION);box_json.put('measured_content_version',box.MEASURED_CONTENT_VERSION);
   end if;physical_boxes.append(box_json);""")
out[str(f/"008_store.sql")]=s
out[str(f/"002_apply_code.sql")]="@@002_admission.sql\n@@003_read.sql\n@@004_boxes.sql\n@@005_load.sql\n@@006_store_weight.sql\n@@007_guard.sql\n@@008_store.sql\n"
out[str(f/"apply.sql")]="@@001_schema.sql\n@@002_apply_code.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_TT_LOAD_BOX_WEIGHT where CASE_BOX_TASK_ID is not null;if n>0 then raise_application_error(-20863,'CASE_MASS_DEPARTURE_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_admission.sql
@@000_before_read.sql
@@000_before_boxes.sql
@@000_before_load.sql
@@000_before_store_weight.sql
@@000_before_guard.sql
@@000_before_store.sql
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_ORIGIN_C;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_COVER_C;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_CASE_F;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_SCALE_F;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_QC_F;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_PALLET_F;
alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_LEGACY_PALLET_F foreign key(BOX_UID)references RRL_PALLETS(UID_PALLET);
alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_LEGACY_ORIGIN_C check(MEASUREMENT_ORIGIN='MANUAL_CONFIRMED');
alter table RRL_TT_LOAD_BOX_WEIGHT drop(PALLET_BOX_UID,CASE_BOX_TASK_ID,FINAL_SCALE_CAPTURE,WAREHOUSE_QC_OPERATION,TARE_WEIGHT_KG,NET_WEIGHT_KG,DEVICE_MODE,COMPOSITION_SIGNATURE,SIGNATURE_VERSION,MEASURED_CONTENT_VERSION,COVERAGE_COMPLETE);
"""
out[str(f/"verify.sql")]="select name,type,line,text from user_errors where name not like 'BIN$%';\nselect object_name,object_type,status from user_objects where status='INVALID'and object_name not like 'BIN$%';\nselect MEASUREMENT_ORIGIN,count(*)from RRL_TT_LOAD_BOX_WEIGHT group by MEASUREMENT_ORIGIN;\n"
print(json.dumps(out,ensure_ascii=True))
