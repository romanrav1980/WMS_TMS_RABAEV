from pathlib import Path
import json
out={}
out["wiki/database/nicora_ni081_route_material_v3_20261011.md"]="""# Адрес и порядок остановок в источнике планового решения
280 / NI08.1 исправляет неполноту sourceV2: snapshot RRL_TT_TIME_API теперь source_contract_version3, существующие ADDR/STDATE/ORD каждого члена СТ. Источник RRL_TT_ROUTE_SOURCE получает эти поля автоматически, удаляя только operations. Смена адреса/порядка/обещанной даты больше не может оставить прежнюю маршрутную оценку текущей. Фактическое CONDITION не добавлено: погрузка/выезд сами по себе не являются изменением планового состава.

Все старые решения/версии/физические факты сохранены. V2-источник не эквивалентен V3, поэтому текущий статус может стать SOURCE_CHANGED и дальнейшее утверждение требует явной новой проверки; автоматического переутверждения нет. Уже совершённые отгрузки/quantity не откатываются. Native пакет получен из liveOracle package body, а не старого архива, paired rollback исходного body; spec не менялся. Изменён только snapshot/result sourceversion. Все объекты VALID.

Actualown33564 имеет две плановые паллеты M270. V3 содержит address/date/ordinal; временный адрес и ORD+10 под CONFIG6 каждый меняют hash/route_status, внешний rollback восстанавливает точный hash и оригинальные поля. П20/Н20 неизменён, история route259/time259 не переписана. SQL scoped member query0.820ms/5/20buffers: решение transport/Oracle сохранить TT-index/bound200 и прежний sourceJSON, без нового индекса/кеша. Привязка roadmatrix/окна/правовые нормы и independentQwen остаются открыты.
"""
for path,line in [
("wiki/index.md","- [Адрес и порядок в источнике маршрута](database/nicora_ni081_route_material_v3_20261011.md):280 native sourceV3/старые решения сохранены/сдвиг адреса или ORD требует пересмотра."),
("wiki/index.md","- [Проект источника маршрута V3](database/nicora_ni081_route_material_v3_design_20261011.md):280 зафиксирован пробелV2 и граница сохранения физической истории."),
("wiki/log.md","2026-10-11:280 liveNativeTIMEbody snapshotsourceV3 adds originalADDR/STDATE/ORD; routeSourceinheritswithoutOPS. V2decisions retained butnotcurrentSource; no autoapproval/physicalrollback. Actualown33564 twoM270members address/ORD temporaryCONFIGmutations hashchanged/sourceSTALE, rollbackexactrestore/protected20-20. SQL0.820ms5/20buf keepexistingTTbound200. NativeallVALID/specunchanged/pairedrollback/manifest override; no driverlaw/storewindow claim."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni08_1.md","11.10.2026:280 SourceV3 включает существующие адрес/дату/порядок остановок. Изменение маршрута делает прежнее утверждение устаревшим, не меняя физических фактов; старые решения сохранены. Own33564 адрес/ORD под rollback проверены, источник восстановлен/P20H20. Общий допуск по дорожному времени/окнам остаётся."),
("wiki/runbooks/nicora_active_work.md","Latest280 nativeTIME sourceV3 (ADDR/STDATE/ORD) allVALID, pairedrollback/livebody. tmp/case280 notbirth: own33564 M2702planningmember address/ORD perturbations eachrolledback/hashrestored. Oldtime/routeV2decisions preserved nowstale; never autoapproveotherTT/undo physicalfacts. Manifest currentTIME component originalspecV2+body280 override, bundle regenerateONLY. App279providers classify actualprofiletime vsSPEED50, localroadproviders unavailable. Next readonlyexistingroute roadlegs andunknown provenance/currentTTsource.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native279/app279/","current native280/app279/")
out["wiki/runbooks/nicora_active_work.md"]=out["wiki/runbooks/nicora_active_work.md"].replace("Native manifest276:","Native manifest280:")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));j["additional_scripts"].append("../2026-10-11_ni081_route_material_v3/001_body.sql");out[str(p)]=json.dumps(j,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI08.1").setdefault("implementedSlices",[]).append("280 native sourceV3 originalADDR/STDATE/ORD invalidates changedroute oldtime; current facts retained/actualownmutation rollback")
out[str(p)]=json.dumps(j,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI08.1"/"280_route_source_v3.md")]="# Qwen280\nNative sourceV3 includes ADDR/STDATE/ORD, neither guessedrouting norphysicalexecutionstatus. Changeoriginalplannedaddress/order -> oldroute/time SOURCE_CHANGED; rollback restoreshash. Original route259/time259 remainimmutableV2, noautoapproval/no physicalundo. Afterloading review rerereads actualnative proof; olddeparted history retained. CurrentWARE rights/bounds200/source hash actualcargo retained. Own33564M2702pallet mutation authorpassed underCONFIGrollback, independenttime approval+browser pending.\n"
out["db/migrations/2026-10-11_ni081_route_material_v3/002_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-280-route-material-source-v3'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original address date and order in time-route sourceV3',sysdate,user,
'db/migrations/2026-10-11_ni081_route_material_v3/001_body.sql','db/migrations/2026-10-11_ni081_route_material_v3/rollback.sql','APPLIED',
'Livebody no spec change; currentADDR/STDATE/ORD hash, oldV2decisions preserved stale, no physicalrollback. Actualown33564 two members address/ordinal perturbations rollbackexact; SQL0.820ms5/20buf P20H20.');
commit;
"""
print(json.dumps(out,ensure_ascii=True))
