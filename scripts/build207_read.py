from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_case_mass");out={}
s=(f/"000_before_admission.sql").read_text(encoding="utf-8")
s=s.replace("package RRL_STOCK_HU_CMD) as","package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_READ,package RRL_STOCK_LOAD_BOX_CORE) as",1)
s=s.replace(" function preserve_case(p_task number)return number;"," function preserve_case(p_task number)return number;\n function mass_json(p_task number)return clob;",1)
pos=s.rindex("\nend;\n/")
s=s[:pos]+"""
 function mass_json(p_task number)return clob is
  identifier varchar2(150);qc_op varchar2(100);carrier varchar2(150);current_version number;needed number;
  qc json_object_t;proof json_object_t;result_json json_object_t:=json_object_t();wire clob;capture_key varchar2(64);measured_version number;signature_value varchar2(64);
 begin
  select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end,s.PALLET_UID,s.WEIGHT_QC_OPERATION_ID,c.SSCC,c.CONTENT_VERSION
   into needed,identifier,qc_op,carrier,current_version from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID
   left join RRL_SBORKA_PALLETS s on s.ID=c.LEGACY_SBORKA_PALLET_ID where c.CASE_PICK_TASK_ID=p_task;
  if needed=0 or identifier is null or qc_op is null then return null;end if;
  qc:=json_object_t.parse(RRL_STOCK_QC_GATE.status_json(identifier));
  if not qc.get_boolean('ready')then return null;end if;
  signature_value:=qc.get_string('composition_signature');
  select c.RESULT_JSON,c.CAPTURE_KEY,u.CASE_CONTENT_VERSION into wire,capture_key,measured_version
   from RRL_WH_FINAL_SCALE_USE u join RRL_WH_SCALE_CAPTURE c on c.CAPTURE_KEY=u.CAPTURE_KEY
   where u.STOCK_OPERATION_ID=qc_op and u.CASE_PICK_TASK_ID=p_task and u.SIGNATURE_VERSION=3 and u.COMPOSITION_SIGNATURE=signature_value;
  proof:=json_object_t.parse(wire);
  result_json.put('case_task_id',p_task);result_json.put('case_content_version',current_version);result_json.put('measured_content_version',measured_version);
  result_json.put('sscc',carrier);result_json.put('capture_key',capture_key);result_json.put('qc_operation_id',qc_op);
  result_json.put('gross_weight_kg',proof.get_string('weight_kg'));result_json.put('tare_weight_kg',proof.get_string('tare_weight_kg'));result_json.put('net_weight_kg',proof.get_string('net_weight_kg'));
  result_json.put('device_mode',proof.get_string('device_mode'));result_json.put('composition_signature',signature_value);result_json.put('signature_version',3);
  result_json.put('origin','WAREHOUSE_SCALE_QC');result_json.put('measurement_ref','WH.SCALE:'||capture_key);
  return result_json.to_clob;
 exception when no_data_found then return null;
 end;
"""+s[pos:]
out[str(f/"002_admission.sql")]=s
s=(f/"000_before_read.sql").read_text(encoding="utf-8")
s=s.replace("n number;\n  begin\n   if p_depth", "n number;mass_wire clob;mass json_object_t;\n  begin\n   if p_depth",1)
needle="a.put_null('tare_weight_kg');nodes.append(a);"
assert s.count(needle)==1
s=s.replace(needle,"""a.put_null('tare_weight_kg');
   mass_wire:=RRL_WH_FINAL_SCALE_ADMISSION.mass_json(p_task);
   if mass_wire is not null then
    mass:=json_object_t.parse(mass_wire);a.put('scale_qc',mass);a.put('gross_weight_kg',mass.get_string('gross_weight_kg'));a.put('tare_weight_kg',mass.get_string('tare_weight_kg'));a.put('net_weight_kg',mass.get_string('net_weight_kg'));
   end if;nodes.append(a);""",1)
out[str(f/"003_read.sql")]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py");s=p.read_text(encoding="utf-8")
needle='        for node in result["nodes"]:\n            if node["kind"]=="CASE"'
assert s.count(needle)==1
s=s.replace(needle,'        measured_cases={node["case_task_id"] for node in result["nodes"]if node["kind"]=="CASE"and node.get("gross_weight_kg")is not None}\n        for node in result["nodes"]:\n            covered=node["kind"]=="STOCK"and node.get("case_task_id")in measured_cases\n            if node["kind"]=="CASE"')
s=s.replace('            weight += Decimal(node.get("tare_weight_kg") or "0")','            if node["kind"]=="CASE"and node.get("gross_weight_kg")is not None:\n                weight += Decimal(node["gross_weight_kg"])\n            elif not covered:\n                weight += Decimal(node.get("tare_weight_kg") or "0")')
s=s.replace('                if node.get("weight_kg") is None:\n                    unknown += 1','                if covered:\n                    continue\n                if node.get("weight_kg") is None:\n                    unknown += 1',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
