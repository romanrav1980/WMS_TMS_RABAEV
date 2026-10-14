from pathlib import Path
import json
f={}
report="""# 32 · Автоподготовка → существующее назначение рейса

Из текущего результата auto preparation добавлен переход к карточке заказа и прежней форме назначения. По ссылке order_id=2135#sapAssignment читается текущий источник и сохранённый PREPARATION_JSON. Существующий assignPreparedSt вызывает прежний /api/admin/transport/tasks/{trip}/sts; дополнительного отношения заказ–рейс нет.

Для уже подготовленной СТ редактор исходной укладки скрыт и повторная подготовка отключена. Исторический источник18A+18B не показывается как фактическая укладка в одно место. После открытия другого источника требуются его актуальные данные. Старый ручной prepareSapSt блокируется при сохранённом запросе авто или отдельной ручной формы; это не переводит его собственное историческое memory-only состояние в durable протокол.

Добавлен явный просмотр ограничений через существующий /api/transport/preflight/trips/{trip}. ТМС показывает текущие source blockers/массу/места/тип машины и предупреждения. Отсутствующая машина или incomplete состояние не объявляются проверенной вместимостью. Это read-only плановая информация; native назначение вновь проверяет текущие данные под блокировками. Погрузка/температура/выезд имеют отдельные условия.

Actual1132: retainedown33571, vehicleQC241ede877f6d1, Спланирован/unbilled. Read-only additionalSAP_2135: две строки641507/641508, два места,24kg, capacity/type CHECKED. operational_admission=false; source2135 остаётся unassigned. Assign/write не выполнялись.

Actual1135 metadata: температурные правила уже есть в RRL_RECEIPT_SKU_RULE и CELL_RULE, термофакты межскладского потока/зоны. Полей температурного режима SKU/vehicle в первоначально выбранных таблицах нет; это не доказывает отсутствия правил во всей системе. Следующее действиеNI02.2 — переиспользование фактических existing thermal rules/flows, без выдуманных допустимых градусов. TEMP_REGION/TEMP_WEIGHT транспортного плана не считаются температурным нормативом по названию.

SQL current preflight/native check49.219ms/394buffers; bounded current_sources52.287ms/856buffers. Решение владельца transport: оставить текущие200ST/5000rows limits и equality/native paths; bulk/correlated-load-proofs rewrite backlog при подтверждённом росте, новый индекс по одному dev случаю не вводить. Это не нагрузочное измерение.

Browser43 до исправления показывает prepared source/FF2PLANNED0, но также старый редактор; screenshot сохраняется как промежуточный. Финальный screenshot44 не получен: Chrome2 стал недоступен. Исправление1133/1134 прошлоJS syntax; не считать визуальную проверку завершённой. UIintent1122 после bridge PASS.

[Карта проекта](../../../wiki/subprojects/retailcase.md). Все18 спринтов ещё не закрыты, GitHub не обновлялся.
"""
f["reports/retailcase/2026-10-13/32-auto-existing-assignment-report.md"]=report
f["reports/retailcase/2026-10-13/32-auto-existing-assignment-evidence.json"]=json.dumps({"preflight":json.loads(Path("tmp/read1132_transport_constraints.json").read_text(encoding="utf-8")),"metadata_sql":json.loads(Path("tmp/read1135_temperature_metadata.json").read_text(encoding="utf-8"))},ensure_ascii=False,indent=2)+"\n"
p=Path("reports/retailcase/2026-10-13/index.html");f[str(p)]=p.read_text(encoding="utf-8").replace("</main>","<article><h2>32 · Автоподготовка → прежний рейс</h2><p>Карточка сохранённой СТ и текущие ограничения существующего назначения.</p><a href=\"32-auto-existing-assignment-report.md\">Отчёт</a><a href=\"screenshots/43-auto-st-existing-assignment.png\">Промежуточный экран43</a></article></main>")
p=Path("wiki/requirements/retailcase_delivery_v55/README.md");s=p.read_text(encoding="utf-8")
s=s.replace("**Revision 11, 09.10.2026.**","**Revision 53, 13.10.2026.**").replace("Следующий — [NI03.2](execution/active/ni03_2.md).","Текущий — [NI02.2](execution/active/ni02_2.md).")
s="Входная страница: [RETAILCASE — описание, исходники и последние изменения](../../subprojects/retailcase.md).\n\n"+s
s+="\n13.10.2026: самостоятельная автоподготовкаNI02.1 через прежние writers, physicalCASE→QC и UIпереход к existingassignment delivered dev/report30–32. Полная независимая приёмка/внешний ACK/все18спринтов не закрыты.\n"
f[str(p)]=s
p=Path("wiki/index.md");f[str(p)]="- [RETAILCASE — единая входная страница](subprojects/retailcase.md): полноеТЗ57, картаисходников, архитектура, текущийплан53 и изменения1113–1134/report30–32.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 /1136: по запросу владельца создана единая RETAILCASE project map с ТЗ/исходниками/архитектурой/последними изменениями. DeliveryREADME синхронизирован53. Report32/preflight1132/SKUthermal metadata1135, optional originalTMS review+savedST bridge; finalbrowser44 unavailable,43intermediate preserved. SlowSQL49.219ms394/52.287ms856 retainbounds/backlogownertransport, noindex. NoGitHub; продолжаетсяNI02.2.\n"
p=Path("wiki/components/retailcase_ni021_auto_preparation_20261013.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n1136: bridge1131–1134 currentreceipt→existingassignment/read-onlypreflight delivered. Already-prepared originaleditor hidden (notoriginaldemand-as-layout); oldprepare blockedbyauto/manual pending. Actual33571 prospective2places/24kg CHECKED, noassignmentwrite. Report32/screenshot43intermediate,final44 unavailableChrome. Projectmap subprojects/retailcase.md introduced.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni02_2.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n13.10.2026/1136: auto receipt→existing order/assignment/read-onlynativepreflight UI. Actual33571 +SAP_2135 prospective2places/24kg/capacitytype CHECKED, nowrite/admission. Existingthermal tables found RRL_RECEIPT_SKU_RULE/CELL_RULE/IWfacts; transportthermal overlap/current shipment guard next, notinventeddegrees. Report32/Chrome final screenshot unavailable.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");f[str(p)]="""# OWNER QUESTION1136 — project description delivered, continue

User asked wherefullproject+latestcode changes, describeandcontinue. Commentary answered precise Wordv57/README/plan53/modularcontract +30/31/bridge. New unified wiki/subprojects/retailcase.md fullentry with modulemap/sourcebaseline/latest1113–1134/reports30–32; registeredindex/log; deliveryREADME now53/currentNI02.2. No finalstop, keepallpreviousobjective.

Report32/evidence saved: UIcurrentauto→selectedorder/sapAssignment/existingassign endpoint +explicitreadonlypreflight button. Oldmanualeditor hidden forpreparedsource, preparebuttondisabled; oldprepare blocked if auto/manualpersistedraw (1134). memory-only legacyoldmanual ownstate remains opengapnotclaimeddurable. Browser43 shows pre-fix misleadingeditor; final44FAILED because Chrome2notavailable, doNOTfake. ExistingCUA browser objectnowunavailable; do not repeatedlyretry/reset/openuserbrowser withoutneed. CouldverifylatestUIprotocol viafocusednode ifneeded, screenshots awaitbrowser.

Actual1132 own33571 planned/unbilled vehicle10059/QC241ede877f6d1, prospectiveSAP_2135 two unassignedSTrows641507/641508,2places24kg checkedcurrentnativecapacity; no newassignwrite. Metadata1135 EXISTINGthermalrules: RRL_RECEIPT_SKU_RULE/CELL_RULE TEMP_MIN/MAX, RRL_INTERWARE_THERMAL_FACT TASK+SKU_TEMP_MIN/MAX, PUTplan tempboundfields, TOPOLOGY_ZONE TEMPERATURE_CLASS. Need inspecttheseexistingmethods/rules/nativecurrentbeforeaddingnewpolicy. TargetedRRL_ARTICULS/FGSKU/VEHICLE no tempcols, but NOTmissingwholethermalconcept. Do nottreatTT TEMP_REGION/TEMP_WEIGHT name asactualtemperature. ContinueNI02.2 requestedremainingtare/thermal/deadline/dock usingexistingcore. SQLpreflight49.219ms394/native &52.287ms856/current_sources retainbounds200/5000/noindex, rewritebacklogownertransport. Encodinglatest1136pending;77070PASS through1130. APIserv1127 currentlatestPython1127 (auto+alias); allnew1131+JS/static only.

Remainingallfullsprintsnotcomplete/noGitHub/commit untilactuallyall/noagents/goals/min80%function. Stable1118auto DONE,2135SAP_2135 two exact18+18/24kg planning0 stock; doNOTfactoryrerun. Original987 currentP20H20/CASE1131v20 qty12&1132v13qty8 twoTOPsQW unchanged. QC alias deliveredreadonlyCP→canonicalv20/report31/screen42/noQCPOST. Report30/screen41 actualauto. Lastscreens43intermediate/currentChromeunavailable.

""" +p.read_text(encoding="utf-8")
print(json.dumps(f,ensure_ascii=True))
