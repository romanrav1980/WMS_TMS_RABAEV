from pathlib import Path
import json,hashlib
f={};root="db/migrations/2026-10-14_ni052_loading_temperature/"
p=Path(root+"002_thermal_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("mode_value varchar2(100);","mode_value varchar2(100);member_values json_array_t:=json_array_t.parse(p_members);")
s=s.replace("  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);\n","",1)
s=s.replace("json_array_t.parse(p_members).get_size","member_values.get_size")
s=s.replace("   select distinct p.WARE_ID,r.ARTICUL,cfg.TEMP_MIN,cfg.TEMP_MAX","   select /*+ leading(member_source p r cfg) use_nl(p r cfg) */ distinct p.WARE_ID,r.ARTICUL,cfg.TEMP_MIN,cfg.TEMP_MAX")
s=s.replace("   from RRL_SBORKA_PALLETS p","   from json_table(p_members,'$[*]'columns(ID number path '$')) member_source\n   join RRL_SBORKA_PALLETS p on p.ID=member_source.ID")
s=s.replace("   where p.ID in(select ID from json_table(p_members,'$[*]'columns(ID number path '$')))\n","")
s=s.replace("  if p_domain is not null then frozen:=","  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);\n  if p_domain is not null then frozen:=")
s=s.replace("  d json_object_t;n number;","  d json_object_t;n number;vehicle_no number;version_no number;observed_no number;reference_value nvarchar2(100);")
s=s.replace("  d:=json_object_t.parse(p_domain);","  d:=json_object_t.parse(p_domain);vehicle_no:=d.get_number('vehicle_id');version_no:=d.get_number('profile_version');\n  observed_no:=signed_decimal(d.get_string('observed_c'));reference_value:=d.get_string('observation_reference');")
s=s.replace("l.VEHICLE_ID=d.get_number('vehicle_id')","l.VEHICLE_ID=vehicle_no")
s=s.replace("values(p_operation,d.get_number('vehicle_id'),d.get_number('profile_version'),signed_decimal(d.get_string('observed_c')),d.get_string('observation_reference'),","values(p_operation,vehicle_no,version_no,observed_no,reference_value,")
f[str(p)]=s
s=Path(root+"000_rrl_stock_hu_load_core_body.sql").read_text(encoding="utf-8")
s=s.replace("destination_wire clob;","destination_wire clob;thermal_value json_object_t;")
point="  p_domain:=json_object_t();"
assert point in s;s=s.replace(point,"  RRL_STOCK_LOAD_THERMAL.compile_confirmation(ids.to_clob,veh.ID,ctx.to_clob,thermal_value);\n"+point,1)
point="  p_domain:=json_object_t();p_domain.put"
s=s.replace("p_domain.put('physical_boxes',physical_boxes);","p_domain.put('physical_boxes',physical_boxes);\n  if thermal_value is null then p_domain.put_null('temperature_at_loading');else p_domain.put('temperature_at_loading',thermal_value);end if;")
s=s.replace("dock_name varchar2(50):=j.get_string('dock');","dock_name varchar2(50):=j.get_string('dock');thermal_wire clob;thermal_element json_element_t;",1)
point="  if places>0 then raise_application_error(-20886,'LOAD_VEHICLE_HAS_ANOTHER_OPEN_TRIP');end if;"
assert point in s
s=s.replace(point,point+"\n  if j.has('temperature_at_loading')then thermal_element:=j.get('temperature_at_loading');if not thermal_element.is_null then thermal_wire:=thermal_element.to_clob;end if;end if;\n  RRL_STOCK_LOAD_THERMAL.assert_current(j.get_array('members').to_clob,vehicle_no,thermal_wire);")
s=s.replace("case_no number:=j.get_number('case_task_id');n number;","case_no number:=j.get_number('case_task_id');n number;thermal_element json_element_t;")
point="  RRL_STOCK_LOAD_BOX_CORE.persist_boxes(p_operation,j.get_array('physical_boxes'),p_actor);"
s=s.replace(point,point+"\n  if j.has('temperature_at_loading')then thermal_element:=j.get('temperature_at_loading');if not thermal_element.is_null then RRL_STOCK_LOAD_THERMAL.persist_confirmation(p_operation,thermal_element.to_clob,p_actor);end if;end if;")
f[root+"003_load_core.sql"]=s
f[root+"005_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1160-loading-temperature' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Current declared SKU thermal limits and manual-at-loading confirmation in existing root load transaction; no sensor inference',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
f[root+"apply.sql"]="@@001_schema.sql\n@@002_thermal_api.sql\n@@004_guard.sql\n@@003_load_core.sql\n@@005_ledger.sql\n"
f[root+"rollback.sql"]="""begin
 raise_application_error(-20863,'LOAD_THERMAL_FORWARD_RECOVERY_REQUIRED: preserve confirmed thermal history and protected loading path');
end;
/
"""
f[root+"verify.sql"]="select NAME,TYPE,LINE,POSITION,TEXT from USER_ERRORS where NAME in('RRL_STOCK_LOAD_THERMAL','RRL_STOCK_HU_LOAD_CORE','RRL_LOAD_THERMAL_FACT_GUARD')order by NAME,TYPE,SEQUENCE;\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_LOAD_THERMAL','RRL_STOCK_HU_LOAD_CORE','RRL_LOAD_THERMAL_FACT_GUARD');\nselect MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-14-1160-loading-temperature';\n"
p=Path("api/wms_api_server/app/modules/transport/api/loading_routes.py");s=p.read_text(encoding="utf-8")
point="class LoadingRequest(BaseModel):"
insert="""class LoadingTemperatureConfirmation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    origin: Literal["MANUAL_AT_LOADING"]
    observed_c: str=Field(strict=True,pattern=r"^-?[0-9]{1,6}(\\.[0-9]{1,3})?$")
    vehicle_profile_version: int=Field(strict=True,ge=1)
    observation_reference: str=Field(strict=True,min_length=1,max_length=100)

"""
assert point in s;s=s.replace(point,insert+point)
s=s.replace("    measurements: LoadMeasures","    temperature_confirmation: LoadingTemperatureConfirmation | None=None\n    measurements: LoadMeasures",1)
s=s.replace('"measurements","physical_boxes"}','"measurements","physical_boxes","temperature_confirmation"}')
point="    if body.physical_boxes:"
s=s.replace(point,"    if body.temperature_confirmation:\n        metadata[\"loading_context\"][\"temperature_confirmation\"]=body.temperature_confirmation.model_dump(mode=\"json\")\n"+point)
f[str(p)]=s
m=json.loads(Path(root+"checkpoint.json").read_text(encoding="utf-8"));m["state"]="PREPARED_NOT_APPLIED"
m["scope"]="Add thermal fact table/API/guard; patch only current shared load core. Departure current confirmation still next, not yet protected."
m["prepared_sha256"]={name:hashlib.sha256(value.encode("utf-8")).hexdigest()for name,value in f.items()if name.startswith(root)}
f[root+"checkpoint.json"]=json.dumps(m,indent=2)
print(json.dumps(f))
