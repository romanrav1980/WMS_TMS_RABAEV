from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni022_vehicle_tare/"
s=Path(root+"000_before_body.sql").read_text(encoding="utf-8")
helper=""" function validated_floor_variants(p_value json_element_t)return json_array_t is
  variants json_array_t;variant json_object_t;limits json_array_t;lim json_object_t;
  code_value varchar2(40);type_id number;places number;n number;keys json_key_list;
  el json_element_t;
  type seen_map is table of boolean index by varchar2(100);seen_codes seen_map;seen_types seen_map;
 begin
  if p_value is null or not p_value.is_array then raise_application_error(-20886,'VEHICLE_TARE_VARIANTS_ARRAY_REQUIRED');end if;
  variants:=treat(p_value as json_array_t);
  if variants.get_size<1 or variants.get_size>20 then raise_application_error(-20886,'VEHICLE_TARE_VARIANTS_BOUND_20');end if;
  for i in 0..variants.get_size-1 loop
   el:=variants.get(i);
   if not el.is_object then raise_application_error(-20886,'VEHICLE_TARE_VARIANT_OBJECT_REQUIRED');end if;
   variant:=treat(el as json_object_t);keys:=variant.get_keys;
   if keys.count!=2 or not variant.has('code')or not variant.has('limits')then
    raise_application_error(-20886,'VEHICLE_TARE_VARIANT_FIELDS_REQUIRED');end if;
   el:=variant.get('code');
   if not el.is_string then raise_application_error(-20886,'VEHICLE_TARE_VARIANT_CODE_REQUIRED');end if;
   code_value:=variant.get_string('code');
   if code_value is null or not regexp_like(code_value,'^[A-Za-z0-9_.:-]{1,40}$')then
    raise_application_error(-20886,'VEHICLE_TARE_VARIANT_CODE_REQUIRED');end if;
   if seen_codes.exists(code_value)then raise_application_error(-20886,'VEHICLE_TARE_VARIANT_CODE_DUPLICATE');end if;
   seen_codes(code_value):=true;seen_types.delete;
   el:=variant.get('limits');
   if not el.is_array then raise_application_error(-20886,'VEHICLE_TARE_LIMITS_ARRAY_REQUIRED');end if;
   limits:=treat(el as json_array_t);
   if limits.get_size<1 or limits.get_size>8 then raise_application_error(-20886,'VEHICLE_TARE_TYPES_BOUND_8');end if;
   for k in 0..limits.get_size-1 loop
    el:=limits.get(k);
    if not el.is_object then raise_application_error(-20886,'VEHICLE_TARE_LIMIT_OBJECT_REQUIRED');end if;
    lim:=treat(el as json_object_t);keys:=lim.get_keys;
    if keys.count!=2 or not lim.has('pallet_type_id')or not lim.has('max_places')then
     raise_application_error(-20886,'VEHICLE_TARE_LIMIT_FIELDS_REQUIRED');end if;
    el:=lim.get('pallet_type_id');
    if not el.is_number then raise_application_error(-20886,'VEHICLE_TARE_INTEGER_TYPE_REQUIRED');end if;
    el:=lim.get('max_places');
    if not el.is_number then raise_application_error(-20886,'VEHICLE_TARE_INTEGER_PLACES_REQUIRED');end if;
    type_id:=lim.get_number('pallet_type_id');places:=lim.get_number('max_places');
    if type_id is null or type_id<1 or type_id!=trunc(type_id)or places is null or places<1 or places>1000 or places!=trunc(places)then
     raise_application_error(-20886,'VEHICLE_TARE_POSITIVE_INTEGER_LIMIT_REQUIRED');end if;
    if seen_types.exists(to_char(type_id,'TM9'))then raise_application_error(-20886,'VEHICLE_TARE_TYPE_DUPLICATE');end if;
    seen_types(to_char(type_id,'TM9')):=true;
    select count(*)into n from RRL_PALLET_TYPE where PALLET_TYPE_ID=type_id and ACTIVE=1;
    if n!=1 then raise_application_error(-20886,'VEHICLE_TARE_ACTIVE_TYPE_REQUIRED');end if;
   end loop;
  end loop;
  return variants;
 end;
"""
point=" procedure configure(p_request";assert s.count(point)==1;s=s.replace(point,helper+point)
s=s.replace("keys.count not in(10,12)","keys.count not in(10,11,12,13)")
s=s.replace("'temp_min_c','temp_max_c')","'temp_min_c','temp_max_c','floor_variants')")
s=s.replace("thermal_min varchar2(100);","floor_value json_object_t;floor_variants json_array_t;\n  thermal_min varchar2(100);")
point="  current_version:=current_version+1;";assert s.count(point)==1
s=s.replace(point,"  if d.has('floor_variants')then floor_variants:=validated_floor_variants(d.get('floor_variants'));end if;\n"+point)
point="  j.put('status','CONFIGURED');";assert s.count(point)==1
s=s.replace(point,"""  if floor_variants is not null then
   floor_value:=json_object_t();floor_value.put('variants',floor_variants);
   floor_value.put('basis','FLEET_DECLARED_FLOOR_VARIANTS');floor_value.put('evidence_reference',reference_value);
   j.put('floor_capacity',floor_value);
  end if;
"""+point)
f[root+"001_profile_variants.sql"]=s
f[root+"002_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1179-vehicle-tare-variants' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit floor loading variants by existing active tare types through versioned vehicle profile; no derived area capacity',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
f[root+"apply.sql"]="@@001_profile_variants.sql\n@@002_ledger.sql\n"
f[root+"rollback.sql"]="@@000_before_body.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-1179-vehicle-tare-variants';\n/\n"
f[root+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_VEHICLE_PROFILE_API';\nselect OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_VEHICLE_PROFILE_API';\n"
p=Path("api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py");s=p.read_text(encoding="utf-8")
point="class VehicleProfileRequest"
models="""class FloorTypeLimit(BaseModel):
    model_config=ConfigDict(extra="forbid")
    pallet_type_id: int=Field(strict=True,gt=0)
    max_places: int=Field(strict=True,ge=1,le=1000)

class FloorLoadingVariant(BaseModel):
    model_config=ConfigDict(extra="forbid")
    code: str=Field(strict=True,pattern=r"^[A-Za-z0-9_.:-]{1,40}$")
    limits: list[FloorTypeLimit]=Field(min_length=1,max_length=8)

    @model_validator(mode="after")
    def unique_types(self) -> "FloorLoadingVariant":
        ids=[limit.pallet_type_id for limit in self.limits]
        if len(ids)!=len(set(ids)):
            raise ValueError("Тип тары повторяется в варианте загрузки")
        return self

"""
assert point in s;s=s.replace(point,models+point,1)
s=s.replace("    reason: str=","    floor_variants: list[FloorLoadingVariant] | None=Field(default=None,min_length=1,max_length=20)\n    reason: str=",1)
point='    @model_validator(mode="after")\n    def temperature_pair'
insert="""    @model_validator(mode="after")
    def unique_variants(self) -> "VehicleProfileRequest":
        if "floor_variants" in self.model_fields_set:
            if self.floor_variants is None:
                raise ValueError("Укажите варианты загрузки или исключите поле")
            codes=[variant.code for variant in self.floor_variants]
            if len(codes)!=len(set(codes)):
                raise ValueError("Коды вариантов загрузки должны различаться")
        return self

"""
assert point in s;s=s.replace(point,insert+point,1)
s+='''

@router.get("/vehicle-profiles/tare-types")
def tare_types(user: AdminUser=Depends(require_permission("transport_dispatch_view")),
               service: VehicleProfilePort=Depends(vehicle_profile_service))->list[dict[str,Any]]:
    try:return service.tare_types(user.username)
    except VehicleProfileError as exc:raise failure(exc)from exc
'''
f[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py");s=p.read_text(encoding="utf-8");s=s.replace("    def read(self,","    def tare_types(self,actor: str)->list[dict[str,Any]]: ...\n    def read(self,",1);f[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py");s=p.read_text(encoding="utf-8")
s+='''
    def tare_types(self,actor: str)->list[dict[str,Any]]:
        with self.gateway.transaction("Read existing active fleet tare catalog")as cursor:
            cursor.execute("set transaction read only")
            cursor.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
             and RRL_HAS_WRIGHT(ID,'transport_dispatch_view')=1""",actor=actor)
            if cursor.fetchone()[0]!=1:
                raise VehicleProfileError("VEHICLE_PROFILE_VIEW_FORBIDDEN","Нет права просмотра автопарка",403)
            cursor.execute("""select PALLET_TYPE_ID,PALLET_TYPE_CODE,PALLET_TYPE_NAME
             from RRL_PALLET_TYPE where ACTIVE=1 order by PALLET_TYPE_ID fetch first 501 rows only""")
            rows=cursor.fetchall()
            if len(rows)>500:
                raise VehicleProfileError("VEHICLE_TARE_CATALOG_BOUND_500","Справочник превышает допустимый размер",409)
            return [dict(zip(("id","code","name"),row))for row in rows]
'''
f[str(p)]=s
f["wiki/database/retailcase_ni022_vehicle_tare_20261014.md"]="""# NI02.2: нормативные варианты загрузки машины
14.10.2026 /1179–1180. Подготовлен additive профиль; применение и результат будут записаны ниже.

Источник: процесс06 ТЗ57 — норматив вместимости конкретной машины по каждому типу тары и допустимым сочетаниям, без вывода из площади пола.

Владелец конфигурации — существующий RRL_VEHICLE_PROFILE_API/HEAD/HIST, право transport_fleet_edit, CFG fence, версия, source hash, неизменная история и точный повтор. Новых таблиц и stock writer нет. floor_variants:1–20 именованных вариантов, в каждом1–8 различных активных RRL_PALLET_TYPE и целое max_places1–1000. В одном варианте перечислены совместно допустимые количества типов; разные варианты альтернативны. Отсутствующий тип не разрешён этим вариантом. Геометрия грузового отсека и температура сохраняются отдельно.

API и карточка используют прежний save/intent/retry. Каталог читает существующий справочник с текущим правом просмотра, граница500. Настройка сама не является допуском погрузки: проверка фактических верхних HU и проводка остаются у существующих native owners; подключение следует отдельным блоком.

Миграция2026-10-14-1179-vehicle-tare-variants: [apply](../../db/migrations/2026-10-14_ni022_vehicle_tare/apply.sql), captured live before-body/checkpoint, paired rollback на прежний защищённый температурный профиль. Старые сохранённые request/results не переписываются.
"""
p=Path("wiki/index.md");f[str(p)]="- [Нормативные варианты тары1180](database/retailcase_ni022_vehicle_tare_20261014.md): существующий versioned vehicle profile/catalog, подготовлены API и native validation; не новый allocator.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1180: подготовлены нормативные варианты загрузки по существующим типам тары через единственный fleet profile owner; checkpoint1179 сохранён, no stock effects. User acceleration: functional slice, bounded verification, short report.\n"
print(json.dumps(f))
