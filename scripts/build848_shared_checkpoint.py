from pathlib import Path
import json
files={}
page="""# NI03.2: одно задание общей целой паллеты

Основа — прежние RRL_STOCK_REPL_SHARED, RRL_STOCK_REPL_NEED, TASK_COMPLETE и sync_wave_tasks. Владелец физических заданий resources, логического ожидания inventory, запись количества только RRL_STOCK_POSTING_API. Новых таблиц нет.

Свежий840 выявил два одинаковых физических задания одной паллеты для двух заказов после отказа вместимости/пересмотра.831–844 projection выделен в resources/infrastructure/wave_task_projection.py: один FULL_PALLET на UID/from/to/quantity в wave, только текущая source reservation/stock location, прежний shared-owner admission, запрет второго активного физического задания источника. BASE задачи не объединяются. Current actorWARE проверяется под прежним metadata CONFIG6.

Уже перемещённое shared HARD могло оставлять RELEASED placeholder с прежней source cell и дважды занимать прогноз вместимости. Inventory public helper снимает только невыданный FULL_PALLET placeholder, если исходный резерв фактически в target, прежний remaining_for_task=0 и нет physical task этого RT. STATUS=CANCELLED/demand0, причина сохранена; DONE/fact за чужое задание не выдумываются. Stock/HARD/units не меняются. Вызывается до continuation selection и физической выдачи под существующей metadata транзакцией.

846 ограничивает maintenance суммарно200 RT на склад; проверяет RUSERS warehouse, группирует выбранные IDs и повторно проверяет факты в UPDATE.847 mock PASS forbidden warehouse и201rows до любого UPDATE, выбранные IDs сохраняются. Не утверждать live positive именно нового ID-bound варианта: actual840 предшествует846, мутация846 уже, gate architecturePASS.

## Реальное исполнение840/845

Уменьшенная вместимость оставила source20/H14,source8/H6,target4/H0 без изменения. Затем valid rebind: targetH4/sourceH2+H6. Один physical task1086 доставил whole20, original continuation6 создан. Отдельная новая волна забрала свободные10 единиц; часть её резерва2 оказалась на втором источнике. Reconcile снял ложное ожидание первого shared arrival, затем ровно одно задание1087 доставило whole8. Итог original owner12/second owner8/third wave10, exact physical replay.845 native VALID, taskDONE20/DONE8, все собственныеP/H0 через штатную cleanup. Старые защищённые источники не изменялись.

HTTP task1087 200DONE; browser734 DOM8EA/fact8/remaining0/disabled. screenshot09 показывает очередь с выбранным1087, не весь detail card. Не аппаратура/независимое испытание. Failed earlier840 attempts были очищены finally; ошибки bound variable и диагностического builder не являются passed.

Gate845 PASS24/bothTS/architecture688-0-76/encodingPASS; pytest-cache rights warning explicit. После846 architecturePASS и targeted847, fullgate не повторялся. SQL shared maintenance17.55мс/126buf и wave discovery26.163мс/84buf до846: retain bounded200/noindex, ownerinventory. SQL projection measurement still open (SQL_TEXT1000 prefix didnotmatch PALLET_RANK); do not claim measured. Partial shared consumer needing additional source/marked/independent races remain open.
"""
files["wiki/components/nicora_ni032_shared_arrival_20261013.md"]=page
report="""# NI03.2: две подачи и общая паллета

13 октября 2026. Исправлены два подтверждённых пробела: выдача двух заданий на одну целую паллету и лишнее ожидание уже прибывшего общего товара при расчёте вместимости. Используются прежние задания и единственное ядро остатков.

Свежий случай840: отказ вместимости без изменения запасов/резервов; затем два физических задания —1086 на20 EA и1087 на8 EA. ОбаDONE. Сохранены резерв исходного заказа12, второго заказа8 и отдельной волны10. Повтор физических команд возвращает сохранённый результат. После случая свой тестовыйP/H очищен штатными командами; история заданий сохранена.

![Очередь с выбранным заданием1087](screenshots/09-second-arrival.png)

Браузерный DOM и HTTP подтвердили1087 DONE/план-факт8EA/остаток0/disabled. Скриншот показывает очередь; карточка прочитана ниже экрана. Это не фото физического сканирования.

Полный quality gate845 PASS24/обаTypeScript/architecture688-0-76/UTF8; предупреждение pytest cache rights не скрыто. После дополнительного сужения maintenance до суммарных200 строк847 PASS bound/currentWARE в mock; положительный live840 выполнен до этого сужения.

SQL maintenance17.55мс/126buffers, discovery26.163мс/84. Решение: сохранить bounded200, индекс сейчас не добавлять. Полный спринт/независимая маркированная конкуренция ещё открыты. Новых реестров/копий Oracle/государственныхACK нет.
"""
files["reports/nicora/2026-10-13/07-two-arrivals-report.md"]=report
files["reports/nicora/2026-10-13/07-two-arrivals-report.json"]=Path("tmp/context845.json").read_text(encoding="utf-8")
p=Path("reports/nicora/2026-10-13/index.html")
files[str(p)]=p.read_text(encoding="utf-8").replace("</main>","<article><h2>07 · Общая паллета и две подачи</h2><p>Задания1086/1087 DONE20/8EA, сохранены три владельца резерва. Лишняя физическая выдача устранена.</p><a href=\"07-two-arrivals-report.md\">Отчёт №7</a> · <a href=\"07-two-arrivals-report.json\">Факты JSON</a><img src=\"screenshots/09-second-arrival.png\" alt=\"Очередь с выбранным заданием1087\"></article></main>")
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json")
plan=json.loads(p.read_text(encoding="utf-8"));inc=next(x for x in plan["increments"]if x["id"]=="NI03.2")
inc["implementedSlices"].append("840-847 existing one physical shared full-pallet task/no stale-source issuance; inventory retires only fully covered unissued arrival placeholder before capacity/continuation; actual capacity refusal/two whole20+8 tasks/original12 other8 third10/replay/cleanup, native845VALID and HTTP/browser1087; total200/currentWARE ID-bound847")
inc["pendingSlices"][0]="Other physical split modes, duplicate retained bindings on the same selected stock, partial shared consumer requiring further sources, marked/concurrent independent multi-continuation acceptance"
files[str(p)]=json.dumps(plan,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni03_2.md")
files[str(p)]=p.read_text(encoding="utf-8")+"\n13.10.2026:840–847 actual capacity refusal unchanged and two original physical20/8 arrivals, one shared-pallet task; fully covered unissued placeholder cancellation (not fake DONE) before capacity/continuation, sum200/WARE bound. Native845VALID/browser1087DONE8EA, own cleanup, gatePASS. [Details](../../../../components/nicora_ni032_shared_arrival_20261013.md). Full/marked/independent partial shared consumer remain.\n"
p=Path("задания на проведения тестов/NI03.2/2026-10-13_sequential_sources.md")
files[str(p)]=p.read_text(encoding="utf-8")+"\nДополнение840–847: воспроизвести один physical FULL_PALLET для shared owners, отсутствие вторичного задания после ARRIVAL, CANCELLED только unissued/remaining0 placeholder, частично покрытый owner остаётся открытым. Проверить global total200 row IDs и currentWARE before UPDATE; positive live846 отдельно от author840. Failed historicalattempts not accepted.\n"
p=Path("wiki/index.md")
files[str(p)]="- [Checkpoint848: общая паллета и две подачи](components/nicora_ni032_shared_arrival_20261013.md): actual840/845 DONE20+8/owner12+8+10, owncleanup, report07/browser1087; sum200-bound847.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md")
files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 checkpoint848: resources sync one shared FULL_PALLET/currentsource/WARE; inventory cancels only fully covered unissued placeholder before capacity/discovery. Actual840/845 two tasks1086/1087DONE20/8, owners12/8/10/replay/cleanup/VALID; HTTP/browser1087. Gate845PASS24/bothTS/encoding; after846 arch688-0-76 +bound847PASS, actual narrowed-ID positive open. Report07/Qwen; no fake task DONE for shared other owner.\n"
p=Path("wiki/runbooks/nicora_active_work.md")
files[str(p)]="""## Checkpoint848 — 13Oct2026

Owner deadline20:00MSK13Oct17:00UTC OR all sprints actuallycomplete. Continue independent functionality, no final before then. Plan34/currentNI03.2, one dev implemented NI03.1/17 fullopen. No agents/goals/DBcopies; no GitHub until actual all complete/excludeSAP.

- Native834/836 VALID, sequential distinct retained sources via original RRL_STOCK_REPL_CONTINUATION. Fresh835 PASS/clean837; fresh840 after fixes PASS capacity refusal unchanged +2physical tasks1086DONE20/1087DONE8/originalowner12+other8+thirdwave10, exact replay/own cleanup. ctx845 is final alreadycleanP/H0/nativeERRORS/INVALIDempty. Neverrerun protected632/773/688 etc. Native source847code unchanged since836.
- New Python resources/infrastructure/wave_task_projection.py and wave_tasks.py uses one canonical FULL_PALLET perUID/from/to/qty within wave/currentRSOURCECELL+REMAIN+existing SHARED.allowed, not second active physicalsource. BASE staysseparate; NVLBASE handlesNULL. CurrentactorWARE checked underexistingmetadataCONFIG6. inventory/public ->shared_arrival_reconciliation.py cancels fullycovered unissued RELEASED FULLplaceholder only(currentH moved totarget/native remaining0/no physical task), not fakeDONE/stock. Calledbefore sync and before ReplenishmentContinuation candidate selection; prevents stale arrival taking capacitytwice. Metadataonly, no secondwriter.
-846 helper total200 row bound (not200waves×200updates), grouped currentselected IDs mutationrestricted JSONselection; currentRUSERSWARE.847mockPASS201/forbiddenbeforewrites/preservedIDs. Actualpositive840 precedes846; new narrowing livepositive notyetdone. Partialsharedconsumerremaining>0 staysopen (currently pointeralreadyattarget mayneedretarget/resume) and marked/concurrent independent branch open.
- Gate845PASS24/bothTS/arch688-0-76/encoding; pytestcachePermissionWarning. After846 archPASS847targetPASS; no broadreruns until needed. APIcurrentHTTP1087 200DONE/automaticreload usable.
- Browser taskTab821857734/evidenceTab sameChrome2 ownadmin. CurrentURL task_id1087#detail. DOMDONE8/fact8/remaining0/completeDisabled; screenshot09queue selected1087 (notfullcard) saved/emitted. reportFs binding. Don't dumpfullAX150rows; evaluate readonly targetedDOM instead. CUA oldbuttonclickstillnoeffect; URLpresetwaiting browser works1/task1080. No hardwareclaims. Resource832 table/currentASSIGNEDdisable838PASS, no actualdispatch.
- report01–07 inownerfolder, current07details/twoarrivals JSON845; newwiki component shared_arrival, plan/card/Qwenupdated848. Native834 rollback/source/SHA saved, no fullbundleapply. SQL845 sharedcleanup17.55ms126buf/discovery26.163ms84 retainboundednoindex. Projection querynotmeasured due1000char SQLTEXT truncation (use prefixWITH CANDIDATES AS/INSERT if needed), don'tclaim measured.
- Avoid script mistakes: build844 initiallytriplequote failed fixed; its globalfixtureSQLbindreplacement corrupted dictvariables, currentcase840 restored from savedtmp/files843.json and only :uid->:p_uid diagnostic/keyword adjusted. Currentcase840 PASS andcleanup. DO NOT rerunoneshot builders. Fixturecurrent capacitydiagnosticSOURCE_SHELF_PERCENT camefrom explicit0 unlike realnativeNULLsettings; notactualfailure.
- Next actualfunctional gaps: partialsharedconsumerremaining>0 sourcepointeralreadyarrived; mark ownarrival/requeue throughexisting remaining-source mechanism (no fakeDONE). Or relevantNI03.3 completion UI. NI07.2 CASE/nested/slots/sharedCONFIG4proof/dayclose open; source1080 P3H3 protected. RequiredNI02originalsplitter choice/realTTcountries/endpoints/certs unanswered, no falseexternalACK/allclosure.

"""+p.read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
