from pathlib import Path
import json,hashlib
f={};root="db/migrations/2026-10-14_ni052_loading_temperature/"
p=Path(root+"002_thermal_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("mode_value varchar2(100);member_values","mode_value varchar2(100);observed_element json_element_t;member_values")
s=s.replace("  observed:=signed_decimal","  observed_element:=observation.get('observed_c');\n  if observed_element is null or not observed_element.is_string then raise_application_error(-20886,'LOAD_THERMAL_DECIMAL_TEXT_REQUIRED');end if;\n  observed:=signed_decimal",1)
f[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading_status.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..contracts import TransportLoadingError","from ..contracts import TransportLoadingError\nfrom .loading_thermal_read import loading_thermal_read")
s=s.replace('    pending=[row["id"]for row in members if not physically_loaded(row)]','    pending=[row["id"]for row in members if not physically_loaded(row)]\n    thermal=loading_thermal_read(cur,header[1],[row["load_operation_id"]for row in loads])')
s=s.replace('"members":members,"physical_places":loads,','"members":members,"physical_places":loads,"temperature":thermal,')
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.html");s=p.read_text(encoding="utf-8")
point="<fieldset><legend>Отдельные измерения физических коробок</legend>"
insert="""<fieldset><legend>Температура непосредственно при погрузке</legend>
<p id="loadTempProfile">Покажите назначение рейса, чтобы прочитать текущий профиль машины.</p>
<label>Версия температурного профиля<input id="loadTempVersion" readonly></label>
<label>Измеренная температура, °C<input id="loadTempObserved" inputmode="decimal" maxlength="11" placeholder="Например, 3.5"></label>
<label>Основание измерения<input id="loadTempReference" maxlength="100" autocomplete="off" placeholder="Номер записи или прибора"></label>
<label><input id="loadTempConfirm" type="checkbox">Подтверждаю измерение непосредственно при этой погрузке</label>
<p>Обязательно для товара с заданными температурными ограничениями. Ручное подтверждение сохраняется с фактом погрузки; оно не заменяет непрерывный контроль датчиком.</p>
</fieldset>
"""
assert point in s;s=s.replace(point,insert+point).replace('<script src="transport-loading.js">','<script src="transport-loading.js?v=20261014-1163">')
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.js");s=p.read_text(encoding="utf-8")
point="  trip=data;"
insert="""  const profile=data.temperature?.vehicle_profile,capability=profile?.profile?.temperature_capability;
  el("loadTempVersion").value=profile?.state==="READY"&&capability?String(profile.version):"";
  el("loadTempProfile").textContent=profile?.state==="READY"&&capability?
   "Текущая версия "+profile.version+": возможности машины "+capability.temp_min_c+" … "+capability.temp_max_c+" °C. Фактическое измерение подтвердите отдельно.":
   "Температурные возможности текущей машины не подтверждены. Для температурного товара настройте профиль автомобиля.";
"""
assert point in s;s=s.replace(point,point+"\n"+insert)
point="    const boxes=window.wmsPhysicalBoxes.collect();"
insert="""    const observed=el("loadTempObserved").value,reference=el("loadTempReference").value;
    if(observed||reference||el("loadTempConfirm").checked){
     const version=Number(el("loadTempVersion").value);
     if(!el("loadTempConfirm").checked||!Number.isSafeInteger(version)||version<1||!reference.trim()||!/^-?[0-9]{1,6}(\\.[0-9]{1,3})?$/.test(observed))throw new Error("Подтвердите текущее измерение, основание и действующий температурный профиль машины.");
     body.temperature_confirmation={origin:"MANUAL_AT_LOADING",observed_c:observed,vehicle_profile_version:version,observation_reference:reference};
    }
"""
assert point in s;s=s.replace(point,insert+point)
s=s.replace("  if(!pending||busy)return;busy=true;controls();const saved=pending;","  if(!pending||busy)return;const saved=pending,raw=localStorage.getItem(key);\n  if(key!==scope()||raw!==JSON.stringify(saved)){status('Сохранённая команда изменилась. Отправка остановлена.');return;}\n  busy=true;controls();")
s=s.replace("   localStorage.removeItem(key);","   if(key!==scope()||localStorage.getItem(key)!==raw)return;\n   localStorage.removeItem(key);")
s=s.replace("  }catch(e){if(key===scope()){","  }catch(e){if(key===scope()&&localStorage.getItem(key)===raw){")
# Keep fields after unknown outcome; clear only after same confirmed command.
s=s.replace('pending=null;composition=null;window.wmsPhysicalBoxes.render(null);','pending=null;composition=null;el("loadTempObserved").value="";el("loadTempReference").value="";el("loadTempConfirm").checked=false;window.wmsPhysicalBoxes.render(null);',1)
f[str(p)]=s
p=Path("wiki/database/retailcase_ni052_loading_temperature_design_20261014.md");f[str(p)]=p.read_text(encoding="utf-8")+"""
## Подготовленная реализация1162–1163

RRL_STOCK_LOAD_THERMAL вычисляет диапазоны member ST и текущую версию профиля, повторно проверяет frozen результат под CONFIG/vehicle/TT locks. RRL_TT_LOAD_THERMAL_FACT имеет FK к исходному физическому load и профилю; запись возможна только из общего load core с rootcontext/lock/privatewriting flag, UPDATE/DELETE запрещены. Факт создаётся после исходного loadfact в той же транзакции; ошибка отменяет оба и товарное движение.

Для SKU с заданным пределом подтверждение обязательно. Если ни у одной SKU не задан диапазон, прежний поток не получает выдуманный режим; отсутствие правила сохраняется как неподтверждённое. Смешанный набор фиксирует configured/unconfirmed SKU counts; температурная пригодность всех неизвестных SKU не заявляется. Один открытый предел поддерживается точно; обратный диапазон отклоняется.

Typed API поддерживает новый блок отдельно от старых полей. Отсутствующий блок не добавляет null/новые ключи в старый canonical request, поэтому прежние сохранённые повторы совместимы. Raw loading UI читает действующий профиль, требует ручное подтверждение и сохраняет точный запрос до отправки. История читается boundedIN≤200 после текущих складских прав в том же READ ONLY снимке.

Пакетная миграция подготовлена, ещё не применена. Capture/checkpoint + SQL/verify сохранены. Rollback намеренно отклоняет возврат к незащищённому старому core; использовать исправление вперёд, сохраняя температурную и товарную историю. Native runtime/физический случай и отдельная departure проверка ещё не выполнены.
"""
p=Path("wiki/index.md");f[str(p)]="- [Prepared1162–1163: температура общей погрузки](database/retailcase_ni052_loading_temperature_design_20261014.md): native pre-effect recheck/atomic immutable fact/scoped read/typed API/UI; apply pending.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1162–1163: prepared sharedload thermalconfirmation, current declaredSKU/profile/version/CFG recheck beforegoods, immutable rootowned sameTX fact; typedHU/single/reconciliation API preserves absentblock canonical hash, readonly bounded thermalhistory/currentvehicleprofile andrawUI/currentstorageguards. Captured live originalcore used; not applied/nativephysical notverified/departure next. No hardwareproof or fullsprintclaim.\n"
p=Path(root+"checkpoint.json");m=json.loads(p.read_text(encoding="utf-8"))
m["prepared_sha256"]={str(p):hashlib.sha256((f.get(str(p)) or p.read_text(encoding="utf-8")).encode("utf-8")).hexdigest()for p in Path(root).glob("*.sql")}
f[str(p)]=json.dumps(m,indent=2)
print(json.dumps(f))
