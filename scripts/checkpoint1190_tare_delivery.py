from pathlib import Path
import json
f={}
r=json.loads(Path("tmp/read1187_vehicle_floor_rule.json").read_text(encoding="utf-8"))
p=Path("reports/nicora/2026-10-13/36-vehicle-tare-variants-report.md")
f[str(p)]="""# Вместимость машины по типам тары —14 октября2026
В существующую карточку машины добавлены нормативные варианты загрузки: разные типы тары и целые предельные количества, совместно допустимые внутри одного варианта. Форма использует готовый справочник; площадь пола не подменяет норматив.

Сохранение выполнено прежним RRL_VEHICLE_PROFILE_API/HEAD/HIST с правом, версией, source hash и точным повтором. Существующая машина10100 получила только тестовую редакцию профиля2; температура−20.125…6.25 сохранена. Проверены откат, повтор и конфликт изменённого тела. После commit проверка1182 ошибочно сравнила весь температурный объект с изменившейся ссылкой на основание;1183 перечитал тот же сохранённый профиль, не создавая новый.

Прежний RRL_TRANSPORT_PLAN_RULES.check_vehicle теперь использует единый native норматив. Отдельные варианты нельзя складывать:8поддонов+4тележки допустимо;1поддон+5тележек несовместимо. Пройдены6 адресных вариантов. Сохранённый SAP_2135 имеет2 места без подтверждённых типов: preview показывает неизвестность, окончательная проверка отказывает. Это проверка общего rule owner, не факт успешного назначения/погрузки.

Текущая стадия подтверждает один действующий CASE на подготовленное место. Уже загруженные TOP и сложные связи пока дают неизвестность; подтверждённый физический TOP/HU — следующий блок. Для машин без матрицы остаётся прежнее PALLETS-ограничение. Масса, тип/гидроборт, адреса и сроки сохранены. Новых stock writer/таблиц/allocator нет.

Native validation1187 пройдена после исправления Oracle19c JSON_ARRAY_T TREAT-cast и размещения результата floor_capacity; текущие изменённые пакеты без ошибок. TypeScript и архитектура703/0циклов/76долгов прошли. Сценарий не является независимой приёмкой полного спринта.

SQL нового boundedIN-запроса:5.472мс/31.33buffers. Решение: оставить200bindST/5000мест и существующие ключи; новый индекс не нужен, ownertransport. Защищённые остаткиP20/H20 не изменены.

[Экран](screenshots/49-vehicle-tare-variants.png) · [Мобильный экран](screenshots/50-vehicle-tare-variants-mobile.png). Скриншоты текущего UI/Oracle, без UI-записи.
"""
f["reports/nicora/2026-10-13/36-vehicle-tare-variants-evidence.json"]=json.dumps(r,indent=2)+"\n"
p=Path("wiki/database/nicora_ni022_vehicle_tare_20261014.md");s=p.read_text(encoding="utf-8")
s=s.replace("Подготовлен additive профиль; применение и результат будут записаны ниже.","Установлены профиль1179 и общий норматив1185; текущие packages/errors проверены, исправления1188/1189 включены в SQL.")
s+="\n## Результат1190\n\nActual retained vehicle10100/profile2: saved variants MIXED8EU+4TROL/TROLLEYS20, same temperature numeric bounds; rollback/replay/conflict passed. Native6 rule cases pass; SAP_2135/2unknown rejects final checker, no actual assignment claimed. SQL5.472ms31.33buffers →retain boundedIN/keys/noindex (ownertransport). P20/H20 unchanged. [Report36](../../reports/nicora/2026-10-13/36-vehicle-tare-variants-report.md)/screens49–50. TS/architecture703/0cycles/76 pass; independent/full acceptance pending. Nextphysical TOP type.\n"
f[str(p)]=s
for root in("2026-10-14_ni022_vehicle_tare","2026-10-14_ni022_vehicle_floor_rule"):
 p=Path("db/migrations")/root/"checkpoint.json";d=json.loads(p.read_text(encoding="utf-8"));d.update(state="APPLIED_TARGETED_VERIFIED",evidence="reports/nicora/2026-10-13/36-vehicle-tare-variants-report.md");f[str(p)]=json.dumps(d,indent=2)+"\n"
for root in("2026-10-14_ni052_loading_temperature","2026-10-14_ni052_departure_temperature"):
 p=Path("db/migrations")/root/"checkpoint.json";d=json.loads(p.read_text(encoding="utf-8"));d.update(state="APPLIED_TARGETED_VERIFIED",evidence="reports/nicora/2026-10-13/35-loading-departure-temperature-report.md");f[str(p)]=json.dumps(d,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");d=json.loads(p.read_text(encoding="utf-8"))
for script in("../2026-10-14_ni022_vehicle_tare/apply.sql","../2026-10-14_ni022_vehicle_floor_rule/apply.sql"):
 if script not in d["additional_scripts"]:d["additional_scripts"].append(script)
f[str(p)]=json.dumps(d,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");d=json.loads(p.read_text(encoding="utf-8"));d["planRevision"]=56
d["deliveryEstimate"]={"basis":"preliminary_owner_requested_2026-10-14_not_measured","remainingDevelopmentHours":[80,160],"excludes":"real external connection/owner acceptance depends on access/data","nextReview":"after two further functional blocks"}
ni=next(s for s in d["sprints"]if s["id"]=="NI02")
ni["autoPalletSplit"]="Owner authorised13Oct; current V2 whole-box/current-temperature automatic calculation and same legacy writer delivered1118/1148"
ni["pendingSlices"]=["Калибровка реальных норм/ограничений автоукладки; физический TOP/type норматив тары; deadline сборки/ворота через готовые owners; реальное ERP согласование."]
ni["changeRequired"]="Сохранить реализованный авторасчёт и прежнее назначение; довести физический TOP/type норматив тары и deadline сборки/ворота без второго планировщика."
for item in("1118 automatic preparation exact36EA/2places/shared writer/race/replay/rollback;1148 V2 temperature grouping","1172 manual loading/departure thermal guard/shared Root/facts/current UI;1173 bounded query","1183 versioned fleet tare variants/current UI;1187 shared native final planning check/unknown refusal"):
 if item not in ni["implementedSlices"]:ni["implementedSlices"].append(item)
f[str(p)]=json.dumps(d,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.md");s=p.read_text(encoding="utf-8").replace("**Revision 55,","**Revision 56,",1)
point="## Фактическое обновление 12 октября"
s=s.replace(point,"## Текущий блок14 октября /1190\n\nАвторасчёт1118/V21148, физическая температура погрузки/выезда1172 и нормативный профиль/общая проверка тары1187 реализованы в dev. Следом — подтверждённый тип физического TOP/HU и deadline сборки/ворота через existing owners. [Отчёт36](../../../reports/nicora/2026-10-13/36-vehicle-tare-variants-report.md). Предварительная оценка по запросу владельца:80–160часов оставшейся разработки, без срока получения внешних доступов; ещё не измеренный прогноз. Полные спринты автоматически не закрыты.\n\n"+point,1);f[str(p)]=s
p=Path("wiki/subprojects/nicora.md");s=p.read_text(encoding="utf-8");s+="\n## Норматив тары1190\n\nКарточка конкретной машины хранит варианты сочетаний готовых типов тары; прежняя final проверка ТМС использует единый норматив и отказывает при неизвестном типе. [Report36](../../reports/nicora/2026-10-13/36-vehicle-tare-variants-report.md), экраны49–50, [план56](../requirements/nikora_delivery_v55/implementation_plan.md). Следом физический TOP/HU и сроки.\n";f[str(p)]=s
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni02_2.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n14.10.2026/1190: loading/depart thermal actual33636 and normative tare fleet profile/common final planning rule implemented; source/type unknown refused. [Report36](../../../../../reports/nicora/2026-10-13/36-vehicle-tare-variants-report.md). Next physicalTOP type/deadline; full sprint remains open.\n"
p=Path("wiki/index.md");f[str(p)]="- [Delivered1190: норматив тары](database/nicora_ni022_vehicle_tare_20261014.md): currentfleet/UI/nativefinalcheck/6cases/unknownrefusal/report36/screens49–50; plan56, TOP next.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1190: normative tare variants profile/UI/native checker delivered1183/1187; fixed JSON cast and result insertion, protectedP20H20, newquery5.472ms31buffers/noindex; report36/screens49–50, checkpoints APPLIED, plan56. User asked total estimate80–160h preliminary; continue TOP/type then deadlines. No agents/noGithub/full sprint notclaimed.\n"
p=Path("wiki/runbooks/nicora_active_work.md");f[str(p)]="# CHECKPOINT1190 — норматив тары delivered\n\nLatestuser asks estimate and continue; answered preliminary80–160h development/externalaccess separate. Delivered1179profile and1185native rule, fixes1188arrayTREAT/1189result location includedfinalSQL. case1182 committedown retainedvehicle10100profile2 then assertion ref changed; resume1183DONE numerictemp unchanged, no recreate. Native readonly11876cases/SAP_21352unknown finalrefused/P20H20/query5.472ms31buffers. CurrentUI49/50 screenshots/report36, TS+arch703PASS, plan56. Source manifest addsprotectedthermal+newtare applies; rebuildbundle notapply. NextphysicalTOP/HUtype anddeadline throughexistingowner. Do not rerunfactory1118/1152/1168/1182. Noagents/noGithub untilallcomplete.\n\n"+p.read_text(encoding="utf-8")
p=Path("scripts/case1182_vehicle_tare.py");s=p.read_text(encoding="utf-8");old='assert after["profile"]["temperature_capability"]==before["profile"]["temperature_capability"]';assert old in s;s=s.replace(old,'assert all(after["profile"]["temperature_capability"][k]==before["profile"]["temperature_capability"][k]for k in("temp_min_c","temp_max_c"))');f[str(p)]=s
p=Path("scripts/screenshot1184_vehicle_tare.mjs");f[str(p)]=p.read_text(encoding="utf-8").replace(" await variants.getByDisplayValue;\n","")
f["задания на проведения тестов/NI02.2/2026-10-14-нормативы-тары.md"]="""# Qwen: нормативы тары NI02.2
Материалы: wiki/database/nicora_ni022_vehicle_tare_20261014.md, reports/nicora/2026-10-13/36-vehicle-tare-variants-report.md, migration1179/1185. Задача подготовлена; модель пока не запускалась.

Не создавать новую базу/схему, не выполнять фабрики1118/1152/1168/1182. Текущая машина10100/profile2 — сохранённый dev metadata case. Для read-only проверки допустим scripts/case1187_vehicle_floor_rule.py; показать общий native результат, неизменный P20/H20 и явную неизвестность SAP_2135. Проверить, что разные варианты не складываются и отсутствующий тип не разрешается.

Независимо прочитать права/source hash/version/replay/rollback и сохранение старой temperature API. Физический TOP/HU и реальная погрузка по матрице этой стадией не доказаны. Не объявлять полный спринт принятым. UI читать8088/3000, скриншоты текущей карточки; запись не требуется. Найденные defects записать отдельно с конкретным сценарием.
"""
print(json.dumps(f))
