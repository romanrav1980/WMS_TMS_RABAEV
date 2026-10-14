from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni022_vehicle_temperature/"
s=Path(root+"000_before_body.sql").read_text(encoding="utf-8")
s=s.replace("expected_hash varchar2(32767):=","thermal_min varchar2(100);thermal_max varchar2(100);thermal_lo number;thermal_hi number;thermal json_object_t;\n  expected_hash varchar2(32767):=")
s=s.replace("if keys.count!=10 or op is null","if keys.count not in(10,12) or op is null")
point="  select count(*)into n from RUSERS where ID=p_actor"
insert="""  for k in 1..keys.count loop
   if keys(k) not in('operation_id','vehicle_id','expected_version','expected_source_hash','vehicle_size_class','cargo_length_mm','cargo_width_mm','cargo_height_mm','reason','evidence_reference','temp_min_c','temp_max_c')
    then raise_application_error(-20886,'VEHICLE_PROFILE_UNKNOWN_FIELD');end if;
  end loop;
  if d.has('temp_min_c') or d.has('temp_max_c') then
   if not d.has('temp_min_c') or not d.has('temp_max_c')
    then raise_application_error(-20886,'VEHICLE_THERMAL_BOTH_BOUNDS_REQUIRED');end if;
   if not d.get('temp_min_c').is_string or not d.get('temp_max_c').is_string
    then raise_application_error(-20886,'VEHICLE_THERMAL_DECIMAL_TEXT_REQUIRED');end if;
   thermal_min:=d.get_string('temp_min_c');thermal_max:=d.get_string('temp_max_c');
   if thermal_min is null or thermal_max is null
    or not regexp_like(thermal_min,'^-?[0-9]{1,6}(\\.[0-9]{1,3})?$')
    or not regexp_like(thermal_max,'^-?[0-9]{1,6}(\\.[0-9]{1,3})?$')
    then raise_application_error(-20886,'VEHICLE_THERMAL_DECIMAL_TEXT_REQUIRED');end if;
   thermal_lo:=to_number(thermal_min,'999999D999','NLS_NUMERIC_CHARACTERS=''.,''');
   thermal_hi:=to_number(thermal_max,'999999D999','NLS_NUMERIC_CHARACTERS=''.,''');
   if thermal_lo>thermal_hi then raise_application_error(-20886,'VEHICLE_THERMAL_RANGE_INVALID');end if;
  end if;
"""
assert point in s;s=s.replace(point,insert+point)
point="  j.put('status','CONFIGURED');"
insert="""  if thermal_min is not null then
   thermal:=json_object_t();thermal.put('temp_min_c',RRL_STOCK_PLAN_HELPER.decimal_text(thermal_lo));
   thermal.put('temp_max_c',RRL_STOCK_PLAN_HELPER.decimal_text(thermal_hi));
   thermal.put('basis','FLEET_DECLARED_CAPABILITY');thermal.put('evidence_reference',reference_value);
   thermal.put('measurement_verified',false);j.put('temperature_capability',thermal);
  end if;
"""
assert point in s;s=s.replace(point,insert+point)
f[root+"001_profile_temperature.sql"]=s
f[root+"002_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1149-vehicle-temperature-profile' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Optional explicit Celsius capability through existing versioned fleet profile; no physical temperature fact or goods effect',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
f[root+"apply.sql"]="@@001_profile_temperature.sql\n@@002_ledger.sql\n"
f[root+"rollback.sql"]="@@000_before_body.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-1149-vehicle-temperature-profile';\n/\n"
f[root+"verify.sql"]="select NAME,TYPE,LINE,POSITION,TEXT from USER_ERRORS where NAME='RRL_VEHICLE_PROFILE_API' order by TYPE,SEQUENCE;\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_VEHICLE_PROFILE_API';\nselect MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-14-1149-vehicle-temperature-profile';\n"
p=Path("api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("Field\n","Field,model_validator\n")
s=s.replace("    reason: str=","    temp_min_c: str | None=Field(default=None,strict=True,pattern=r\"^-?[0-9]{1,6}(\\.[0-9]{1,3})?$\")\n    temp_max_c: str | None=Field(default=None,strict=True,pattern=r\"^-?[0-9]{1,6}(\\.[0-9]{1,3})?$\")\n    reason: str=")
point="\ndef failure("
insert="""
    @model_validator(mode="after")
    def temperature_pair(self):
        from decimal import Decimal
        if ("temp_min_c" in self.model_fields_set) != ("temp_max_c" in self.model_fields_set):
            raise ValueError("Оба температурных предела обязательны")
        if "temp_min_c" in self.model_fields_set:
            if self.temp_min_c is None or self.temp_max_c is None or Decimal(self.temp_min_c)>Decimal(self.temp_max_c):
                raise ValueError("Укажите корректный температурный диапазон")
        return self
"""
assert point in s;s=s.replace(point,"\n"+insert+point).replace('body.model_dump(mode="json")','body.model_dump(mode="json",exclude_none=True)')
f[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/finance/VehiclePhysicalProfile.tsx");s=p.read_text(encoding="utf-8")
s=s.replace("reason:string;evidence_reference:string};","reason:string;evidence_reference:string;temp_min_c:string;temp_max_c:string};",1)
s=s.replace("actor:string;evidence_reference:string}};","actor:string;evidence_reference:string;temperature_capability?:{temp_min_c:string;temp_max_c:string;measurement_verified:false}}};")
s=s.replace("reason:string;evidence_reference:string};\ntype Pending","reason:string;evidence_reference:string;temp_min_c?:string;temp_max_c?:string};\ntype Pending")
s=s.replace('evidence_reference:"Основание габаритов"','evidence_reference:"Основание габаритов и температурного диапазона",temp_min_c:"Минимум температуры машины, °C",temp_max_c:"Максимум температуры машины, °C"')
s=s.replace('reason:"",evidence_reference:""','reason:"",evidence_reference:"",temp_min_c:"",temp_max_c:""')
s=s.replace('cargo_height_mm:value.profile?String(value.profile.cargo_height_mm):""','cargo_height_mm:value.profile?String(value.profile.cargo_height_mm):"",temp_min_c:value.profile?.temperature_capability?.temp_min_c??"",temp_max_c:value.profile?.temperature_capability?.temp_max_c??""')
point="  const intent:Pending={body:"
insert="""  const hasTemperature=fields.temp_min_c!==""||fields.temp_max_c!=="";
  if(hasTemperature&&(!/^-?[0-9]{1,6}(\\.[0-9]{1,3})?$/.test(fields.temp_min_c)||!/^-?[0-9]{1,6}(\\.[0-9]{1,3})?$/.test(fields.temp_max_c)||Number(fields.temp_min_c)>Number(fields.temp_max_c))){
   setMessage("Укажите оба температурных предела в °C, до трёх знаков после точки.");return;
  }
"""
assert point in s;s=s.replace(point,insert+point)
s=s.replace("reason:fields.reason,evidence_reference:fields.evidence_reference}};","reason:fields.reason,evidence_reference:fields.evidence_reference,...(hasTemperature?{temp_min_c:fields.temp_min_c,temp_max_c:fields.temp_max_c}:{})}};")
s=s.replace("<h3>Класс и грузовой отсек</h3>","<h3>Класс, грузовой отсек и температурные возможности</h3>")
s=s.replace(' required value={fields[k]}',' required={!k.startsWith("temp_")} value={fields[k]}')
s=s.replace('k==="vehicle_size_class"?40:7','k==="vehicle_size_class"?40:k.startsWith("temp_")?11:7')
s=s.replace('inputMode={k.startsWith("cargo_")?"numeric":"text"}','inputMode={k.startsWith("cargo_")?"numeric":k.startsWith("temp_")?"decimal":"text"}')
s=s.replace("<p>Профиль фиксируется","<p>Температурные пределы задаются парой по подтверждённым возможностям машины. Пустые поля означают отсутствие подтверждённого диапазона; измерением температуры они не являются.</p>\n  <p>Профиль фиксируется")
f[str(p)]=s
print(json.dumps(f))
