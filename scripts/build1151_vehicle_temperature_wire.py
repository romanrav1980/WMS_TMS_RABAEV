from pathlib import Path
import json,hashlib
f={};root="db/migrations/2026-10-14_ni022_vehicle_temperature/"
p=Path(root+"001_profile_temperature.sql");s=p.read_text(encoding="utf-8")
s=s.replace("thermal json_object_t;","thermal json_object_t;thermal_min_element json_element_t;thermal_max_element json_element_t;")
s=s.replace("   if not d.get('temp_min_c').is_string or not d.get('temp_max_c').is_string","   thermal_min_element:=d.get('temp_min_c');thermal_max_element:=d.get('temp_max_c');\n   if not thermal_min_element.is_string or not thermal_max_element.is_string")
f[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..domain.preflight_routes import plan_routes","from ..domain.preflight_routes import plan_routes\nfrom ..domain.temperature_preflight import temperature_preflight")
point='    thermal["vehicle_legacy_mode"] ='
insert="""    current_profile = None
    if vehicle_row:
        current_profile=read_oracle_json(cur.callfunc("RRL_VEHICLE_PROFILE_API.describe_profile",oracledb.DB_TYPE_CLOB,[route["vehicle_id"]]))
    thermal["planning"]=temperature_preflight(thermal,current_profile)
"""
assert point in s;s=s.replace(point,insert+point)
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");s=p.read_text(encoding="utf-8")
point="const thermal=route.temperature_requirements"
# Use exact observed source in next step; don't silently claim UI mutation.
f[str(p)]=s
m=json.loads(Path(root+"checkpoint.json").read_text(encoding="utf-8"))
m["prepared_sha256"]={str(p):hashlib.sha256((f.get(str(p)) or p.read_text(encoding="utf-8")).encode("utf-8")).hexdigest()for p in Path(root).glob("*.sql")}
m["scope"]="Replace captured profile body only; no table/column/trigger changes. Keep original immutable history/replay/config fence. Existing profile base hashes remain unchanged."
m["recovery"]="Restore captured 000_before_body.sql; retained history JSON remains readable and immutable. No database copy or historical inference."
f[root+"checkpoint.json"]=json.dumps(m,indent=2)
p=Path("wiki/database/retailcase_ni022_vehicle_temperature_20261014.md")
f[str(p)]="""# NI02.2 — температурные возможности автомобиля
Миграция: 2026-10-14-1149-vehicle-temperature-profile. Подготовлена; применение ещё не подтверждено.

Существующий RRL_VEHICLE_PROFILE_API расширяется необязательной парой temp_min_c/temp_max_c (десятичные строки в °C). Оба предела и действующее основание обязательны, min≤max. Это заявленные возможности одного общего температурного пространства. Фактическое измерение, настройка холодильника и допуск погрузки отдельны.

Новая версия проходит прежнюю CONFIG fence, transport_fleet_edit, текущую версию и base_hash. Диапазон хранится внутри неизменяемого RESULT_JSON существующего RRL_VEHICLE_PROFILE_HIST; новых таблиц, колонок, quantity writer нет. Старые запросы/профили/хеши/история остаются совместимыми. Профиль без диапазона — неизвестный, BASE_CHANGED не допускает использовать его как подтверждённый.

Preflight читает текущий профиль в том же READ ONLY снимке с требованиями SKU. Точное пересечение диапазона возможностей машины с требованиями товара показывает достижимый диапазон. Это не проверка включения всего диапазона машины внутрь товарного диапазона. Нет общего режима/неизвестный SKU/машина — явный отказ подтверждения температурной совместимости. Measurement/operational admission остаются false.

Снимок исходного тела/спецификации и baseline INVALID: [checkpoint](../../db/migrations/2026-10-14_ni022_vehicle_temperature/checkpoint.json). Apply/rollback/verify рядом. Пакетный откат сохраняет историю JSON, не изменяет остатки. Разрешение владельца: продолжать реализацию всех спринтов в выделенном dev RABAEV.
"""
p=Path("wiki/index.md");f[str(p)]="- [NI02.2 температурный профиль1150–1151](database/retailcase_ni022_vehicle_temperature_20261014.md): existing versioned fleet profile/API/UI, exact capability intersection; prepared, no physical admission.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1150–1151: saved live profile spec/body, prepared backward-compatible optional numeric temperature pair in original versioned API/history; fleet UI and bounded same-snapshot planning intersection. Migration mirrored/checkpointed/rollback captured; application and targeted native checks pending. No new tables or stock effect.\n"
print(json.dumps(f))
