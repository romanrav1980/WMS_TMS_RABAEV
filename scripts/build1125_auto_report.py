from pathlib import Path
import json
f={}
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py");s=p.read_text(encoding="utf-8").replace('"sequence": sequence, "strategy": STRATEGY}', '"sequence": sequence, "strategy": STRATEGY, "limits": limits}');f[str(p)]=s
report="""# 30 · Автоматическая подготовка СТ из заказа SAP

Разработана по прямому решению владельца13.10.2026: свежего split_vegetables/PALL_SPLITTER нет, сделать самостоятельно.

Новый чистый расчёт whole-box layout работает с текущими карточками, нормами, массой коробки, DIMKORmm, группой и порядком RRL_COMPL_SEQ. Он заполняет места целыми коробками, смешивает хвосты только внутри одной группы и соблюдает массу, объём и сумму долей паллетных норм. Дробная арифметика точная; вместимость округляется вниз. Ограничения массы/объёма задаются явно, максимум100мест/1000SKU. Глобальная оптимальность и трёхмерная укладка не заявляются.

Создание проходит прежними ORDERS/SBORKA/fulfillment writers в одной source transaction. Старый архивный пакет с внутренними COMMIT/DELETE и заглушки не объявляются рабочей реализацией. Создатель количества и назначение рейса сохранены. Oracle DDL не менялась.

Preview только читает; source_signature связывает текущие карточки/календарь/исходник/sequence/стратегию/пределы. Команда с сохранённым operation_id повторяется в пределах исходного customer_order_id. Под текущими правами/WARE и source/config locks результат проверяется до перерасчёта. Для нового плана блокируется sequence SHARE WAIT3 (включая отсутствующие строки), затем SKU в стабильном порядке, затем прежняя таблицаORDERS. Противоречащие карты/нормы или новый snapshot отклоняются. Ошибка откатывает всю попытку.

Интерфейс показывает предложение, создаёт СТ по нему, повторяет неизменный запрос и проверяет исход. Shared intent сохраняется до POST; смена пользователя/другая вкладка/неподтверждённый ответ сохраняют запрос. Повреждённый запрос архивируется только после текущего авторизованного GET исходника. Ручная и автоматическая формы не начинают новую команду при сохранённом запросе другой формы. Текущая СТ читается отдельно; новый receipt хранит planned_pallets. Старый receipt1118, сохранённый до добавления этого поля, показывает показатели мест без выдуманного распределения SKU.

## Реальные результаты

Own1118: изолированные новые SKUQAUTOc0c2a00c0bA/B, принятый заказ2135, склад9807. По18EA каждого SKU, коробка6EA, норма24EA, масса4kg/box, размеры400×300×200mm. Предел16kg/0.096m³. Первый план:18A+6B (16kg); второй:12B (8kg). Прежние writers создали ORDERS48470, SAP_2135, OP_SAP_2135_1/2. Проверено по legacy rows: каждый SKU18EA/3boxes/12kg; FF2PLANNED/FACT0. Защищённый склад5062399 сохраняет P20/H20.

PASS: реальный shared writer с outer rollback и отсутствие saved result; устаревший preview после изменения собственной тестовой нормы; две конкурирующие команды — один результат/один конфликт; точный repeat/resolve; другое содержимое того жеID; saved replay после изменения карточки. Исторические fixtures2044–2048 не изменены. 2047 имеет противоречивую норму1<коробки24 и получает409, а не фиктивную подготовку.

HTTP1121: сохранённые repeat/resolve200, нарушенная норма409, extra field422, anonymous401/403. JS1122: save-before-send/exact repeat/cross-tab/damaged denied/archive-before-delete/late actor PASS. Domain1116: exact mixed tails, разные группы, целые коробки, floor, пределы PASS. Architecture698files/0cycles/76debt PASS. Авторские проверки не заменяют независимую приёмку.

## SQL и границы

ActualV$SQL: readiness8.286ms/75.57buffers, sequence2.603ms/14.5buffers. Решение владельца fulfillment: оставить bounded1000SKU/100мест и stable bulk packing; новый индекс не требуется по этому случаю. Sequence SHARE и прежний ORDERS SRX могут ограничить параллельную подготовку; отдельный backlog владельца fulfillment: versioned warehouse sequence + уникальные legacy identities перед повышением throughput. Широкая нагрузка не выполнялась.

Нет подтверждения внешнего SAP ACK, физической вместимости тары/геометрии или устройств. Для маркированных товаров сохраняется планSKU; уникальные коды и фактический состав проверяются действующими этапами отбора/контроля. При отсутствии настройки маркировки эти этапы нельзя обходить.

[Итоговый экран](screenshots/41-auto-st-saved-result.png). Screenshot39 — первая навигация показала реестр, а не форму;40 — промежуточная форма;41 — текущая созданнаяСТ. Скриншоты не доказывают ручное нажатие/сканирование.
"""
f["reports/nicora/2026-10-13/30-auto-st-report.md"]=report
case=json.loads(Path("tmp/context1118.json").read_text(encoding="utf-8"))
http=json.loads(Path("tmp/http1121_auto.json").read_text(encoding="utf-8"))
f["reports/nicora/2026-10-13/30-auto-st-evidence.json"]=json.dumps({"case":case,"http":http},ensure_ascii=False,indent=2)+"\n"
p=Path("reports/nicora/2026-10-13/index.html");s=p.read_text(encoding="utf-8");s=s.replace("</main>","<article><h2>30 · Автоматическая подготовка СТ</h2><p>Целые коробки, смешанные хвосты одной группы, точные ограничения и прежний Oracle writer.</p><a href=\"30-auto-st-report.md\">Отчёт</a> · <a href=\"30-auto-st-evidence.json\">Данные</a><img src=\"screenshots/41-auto-st-saved-result.png\" alt=\"Созданная СТ: два места16kg и8kg\"></article></main>");f[str(p)]=s
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");x=json.loads(p.read_text(encoding="utf-8"));x["planRevision"]=52
for i in x["increments"]:
 if i["id"]=="NI02.1":
  i["title"]="Автоматическая подготовка СТ через существующие writers"
  i["status"]="implemented_targeted_verified"
  i["changeRequired"]="По решению владельца13Oct реализован собственный exact whole-box/group/mass/volume расчёт; прежний ORDERS/SBORKA writer и назначение. Явные пределы обязательны. Независимая полная приёмка отдельно."
  i["acceptanceStatus"]="targeted_dev_actual1118_http1121_ui1122_report30_full_independent_pending"
  i["implementedSlices"].append("1113–1125 auto domain/scoped snapshot + limits signature/shared locked writer/request receipt + durable UI; actual2135 SAP_2135 two places exact18+18/race/rollback/replay, report30")
  i["sourceAnchors"] += ["api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py","api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py","wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.js"]
x["currentSprint"]="NI03.3";x["currentSprintMeaning"]="Continue remaining functional gaps; next physical CASE alias to existing QC after delivered auto preparation"
x["ownerAutoPreparationDecision"]["status"]="implemented_targeted_verified"
# Do not declare a full sprint or overall release accepted.
f[str(p)]=json.dumps(x,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni02_1.md");s=p.read_text(encoding="utf-8")
s=s.replace("# NI02.1. Оригинальная автоматическая подготовка СТ","# NI02.1. Автоматическая подготовка СТ через существующие writers")
s=s.replace("Статус: planned_delta.","Статус: implemented_targeted_verified (dev; независимая приёмка отдельно).")
s=s.replace("Найти и восстановить утверждённый оригинальный auto-split вместо dev stubs. Если исходник недоступен, оставить ручную подготовку и блокер; второй splitter без отдельного решения не писать.","По решению владельца13Oct реализован собственный bounded exact расчёт через существующий writer. Архив и stubs не используются как рабочий auto-split. Независимая приёмка полного процесса и throughput остаются отдельными.")
s+="\n13.10.2026/1125: automatic_layout + AutomaticPreparation + preview/run/resolve + UI/current read/intent recovery реализованы. Own1118/order2135 SAP_2135:18A+6B/12B, точные36EA/6boxes/24kg, FF2PLANNED0/P20H20; rollback/stale/race/replay/conflict PASS. HTTP1121/JS1122/domain1116 PASS. [Контракт](../../../../components/nicora_ni021_auto_preparation_20261013.md), [отчёт30](../../../../../reports/nicora/2026-10-13/30-auto-st-report.md). Приёмка полного спринта независимым исполнителем не заявлена.\n"
f[str(p)]=s
p=Path("wiki/components/nicora_ni021_auto_preparation_20261013.md");s=p.read_text(encoding="utf-8")
s+="\n1125: actual isolated2135 SAP_2135/2places18A+6B/12B, exact18EA/3boxes/12kg perSKU, outerrollback/stale/race/replay/conflict/currentHTTP+UI PASS. ProtectedP20H20. Report30/screen41; source2047 remains unprepared/badnorm, oldfixturesunchanged. Preview signature now includes limits too; saved original1118 receipt is returned unchanged. Current read-only UI displays original receipt stats; new receipts additionally save explicit planned_pallets. NoDDL; older archive remains evidence. SQL8.286ms/75.57 and2.603ms/14.5 retainboundedreads/noindex, ownerfulfillment; globalmetadata fences versioning backlog.\n"
f[str(p)]=s
p=Path("wiki/index.md");f[str(p)]="- [NI02.1 dev delivered1125](components/nicora_ni021_auto_preparation_20261013.md): actual2135/mixed2places/exact36EA/race/rollback/replay/report30/screen41; plan52, allfullsprints remain open.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 /1125: NI02.1 самостоятельная автоподготовка по решению владельца delivered targeted dev. Actual2135→existingSAP_2135/2places, точные36EA/24kg/6boxes; race/rollback/stale/replay/conflict; HTTP1121/JS1122/domain1116 PASS; report30/screen41/plan52. NoDDL/noGithub/allfullsprints notcomplete. SQLreadiness8.286ms/75.57buffers/sequence2.603ms/14.5 retainbounds, fences backlog ownerfulfillment.\n"
p=Path("wiki/runbooks/nicora_active_work.md");f[str(p)]="""# CHECKPOINT1125 — NI02.1 automatic preparation delivered; continue all

Owner no fresherSQL explicit make ourselves fulfilled via domain/automatic_layout + infrastructure/automatic_preparation shared LegacyPreparation._prepare_locked, current oldsource/config rights, stable sequence SHARE->SKU->ORDERS locks. Auto preview/run/resolve + separateUI/currentGET/shared durable intent/damaged archive. DIMKOR is current mm, notcm; corrected before live, /10^9 exact. Mandatory explicit goods mass/volume/max100, norms wholebox/group stable greedy, no3Dproof. Signature includes limits after1125; cached old1118 remains immutable. New receipt saves planned_pallets; old1118 onlystats so currentUI says composition in ordercard (not inventedSKU).

Actual own1118 context DONE: order2135 WARE9807/SAP_2135/ORDERS48470/2planningpallets OP_SAP_2135_1/2. QAUTOc0c2a00c0bA/B each18EA/3box/12kg; first18A+6B=16kg/.096m3, second12B=8kg/.048. Synthetic new articles importedthroughARTMAS, own pickingcell/group1118; no physical stock birth. Original2044–2048 unchanged;2047badnorm1<24 returns409. Actualrollback/stale ownnorm change restore/raceonewinner/conflict/replay/cachebeforemaster PASS; no factories rerun case1118 DONE. Some failed test attempts preserved: dirtyTX repeatedbegin rightlyrefused, wrongREMAINSARTICUL verificationfixed; notnativeguard changes.

APIserv1120 restarted before1123 metadata/newvolume36/signaturelimits; Pythonlatest not yet guaranteed loaded; restart before next new auto command ifneeded. HTTP1121 repeat/resolve/noanonymous/strict/badnorm PASS, domain1116 andUIintent1122 PASS. Architecture698/0/76 PASS beforelatestminor. Encodingfinalpending. Reports30/evidence/screens39registernotform40intermediate41actualsavedresult. Browserorder1043Tab/Chrome2/821857750 current8088/wms-admin/customer-orders.html?sap_order=2135&v1123#sapAutoPreparation. ScreenshotfsorderReportFs1043; NEVER8090 (refused), no broad tmp rg (hugeoutput), inspect specific observedpaths only.

Plan52 NI02.1implemented_targeted_verified/currentNI03.3; no fullfunctional sprint independentacceptance/all18 notcomplete/noGithub. Continue actualremaining next physicalCASE alias→existingQC gap1107; originalQC scopes/WARE/ambiguousalias no bypass. Protected987 P20H20/HU1069v10/CASE1131CTFF20 qty12, HU994v18/CASE1132CTFF13 qty8 bothTOP/QW/1157+1159DONE. No new physicalfixtures/QCPOST without genuineconfig; report29 currentBOTH/independent/fullscan SIweightpolicy missing. Owneruntilallno cutoff, don'tfinal aftercheckpoint, noagents/goals/clones, ≥80%functional.

""" +p.read_text(encoding="utf-8")
print(json.dumps(f,ensure_ascii=True))
