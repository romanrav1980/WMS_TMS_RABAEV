from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8")
files={}
page="""# NI03.3: единая выбранная волна и очередь

886–890: lean GET /api/picking/waves/{id}/header переиспользует выделенный existing SQL header. PickingService get_wave/get_wave_header остаются фасадами. Монолит уменьшен2320→2284 lines, baseline tightened downward; architecture690/0cycles/76 allowances PASS.

WaveQueueReads оборачивает существующие readers в native current actor scope и одну READ ONLY транзакцию. Список: active RUSERS/pick_wave_view; GLOBAL_ADMIN сохраняет заданный фильтр, прочим автоматически свойWARE и отказ явно чужого фильтра. Detail/readiness/reservations/replenishment/tasks проверяют wave scope перед legacy query. Header не подтягивает all composition. Legacy full-detail unbounded order/line lists остаются inventory backlog для крупных волн.

UI deep link вне первых100: header, pinned selected wave, связанные execution/pick/progress/queue. Loading до read отключает старые действия; epoch/actor/API guard игнорирует поздние ответы, saved pending удерживает wave. Source availability скрывается при смене выбора.

Actual889: header403 безorders, admin scoped warehouse20052672 returned8 matching rows; inactive/foreign wave551 denied403 до legacy read. Browser888: selected403/MIXED172 иall3panels403. JS891 delayedA cannot overwriteB/savedB blocksA/no writes. Latest890 pinned/loading browser ожидает; nonadmin ownWARE positive ещё не live proved.

SQL892: header18.61ms/273buf, filtered list22.792ms/37buf, actor/currentright41.049ms/27buf (2executions). Inventory decision retain existingkeys/bounded queue/noindex; sustained>500ms→plan/stats. Не нагрузочная приёмка.
"""
files["wiki/components/nicora_ni033_wave_queue_20261013.md"]=page
files["reports/nicora/2026-10-13/12-wave-queue-report.md"]=page
p="reports/nicora/2026-10-13/index.html";files[p]=read(p).replace("</main>",'<article><h2>12 · Выбранная волна и её очередь</h2><p>Ссылка вне первых100 строк и защита текущего склада.</p><a href="12-wave-queue-report.md">Отчёт №12</a></article></main>')
p="wiki/index.md";files[p]="- [Checkpoint893: очередь волны](components/nicora_ni033_wave_queue_20261013.md): lean header/current actor snapshot, actual889/browser888/JS891, report12/architecture reduced.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint893:886-890 lean header/scoped existing reads/selected outside100/scope epoch/loading/saved wave; actual889 readonly/browser888/JS891; SQL892 retain bounded noindex; PickingService2320→2284 baseline tightened down. Latest890 browser/nonadmin ownWARE positive pending.\n"
p="wiki/requirements/nikora_delivery_v55/implementation_plan.json";plan=json.loads(read(p));plan["planRevision"]=35;plan["currentSprint"]="NI03.3";plan["firstChange"]="Continue original CASE/control/shipping and warehouse-task deltas after866/869/872/877, until20:00MSK13Oct2026 or actual all completion. No false independent/external acceptance."
inc=next(x for x in plan["increments"]if x["id"]=="NI03.3");inc["implementedSlices"].append("886-893 original lean wave header/current actor readonly queue/detail/tasks; selection outside100, stale/loading/pending wave guards; actual889/JS891/browser888; legacy reduced2320 to2284")
files[p]=json.dumps(plan,ensure_ascii=False,indent=2)
p="wiki/runbooks/nicora_active_work.md";files[p]="""## Checkpoint893 — 13Oct2026

Deadline20:00MSK today17:00UTC OR all sprints actuallycomplete. Do not final/stop earlier while independent functionality possible. Plan35/currentNI03.3; all18 not completed. Conditional fullcommit/GitHub onlyAFTERALLcomplete, excludeSAP. No agents/goals/copies. One RABAEV/orcl stockrootACTIVE/compatOFF.

Native852 capacity one physicalincoming;866 same-source binding;869 aggregateowner admission;872 exact post-target closure/allown incoming;877 currentpickscope before replay/afterlocks. AllAPPLIED/VALID, checkpoint/SHA/pairedrollback. Fresh867 wave546/task1099 DONE20 own12/other8/no next, cleaned; related850 wave547 whole20+12 owners12/8/14 cleaned, report10 JSON. Final879 wave551/task1104 after existingCasePickService.ensure helper, native/servicepick release/replay/admin, foreignQA172_KRO read403/native20882 before replay, cleaned. read881 uses originalSERVICE material; prior directbody/service OP conflict correct. Don'tchange saved operation bodies.

UI860-890 modular execution/view/commonintent with separate existingPICK/FINISH keyprefix/validators/correlated result/scope+raw compare/archive+reread. Three-panel workspace. Lean wave headerSQL moved to inventory module; existingqueues/detail/tasks scoped READONLY. Service2320→2284, debt tightened onlydown, architecture690/0/76PASS. Latest890 pinned/loading/requestedhandlers needbrowser refresh; browser888proved403 outside100/all3input403. init queue authhandler stillonce: nextfix clear stalequeue/reload on authchange.

Quality882 PASS24/bothTS/architecture688 (before newreadmodules); cachepermissionwarning. New690archPASS, JS891stale wave/pending, JS861882intentPASS. Read889 readonlyheader403/adminwarehouse8rows/inactive+foreigndenied. Nonadmin ownWARE list positive not live. SQL892 header18.61ms/list22.792ms/actor41.049ms retainboundednoindex. Legacy full detail unboundedorders/lines inventorybacklog, newheader avoids.

Reports01–12, screenshots01–13. BrowserChrome2 taskTab821857734/reportFs currentURL8088/wms-admin/wave-replenishment.html?wave_id=403#waveExecution. goto sameURLmaynotreload; taskTab.reload(). Screenshot13latestcurrent403;12oldcachedscreen. Plain3000React/8089wrongavoid. ReadonlyDOM/screenshot save+emit.

Protected1080/SAP688P3H3/3units6codes; CASE1031/1032P20H20; money107.25/current0 unchanged. Neveroldfactories/cleanup. Current867/879/850 ownP/H alreadyclean. NI03.2 marked/weighted/independent concurrency and physicalsplit residuals open; NI03.3 fullCASE/control/shipping/multi-place and independent acceptance open. NI07.2 CASE/nested/sharedCONFIG4/dayclose open. NI02splitchoice and actualTTcountries/endpoints/certs unanswered; nofakeGovACK.

Next actual890 browser/selected pin, routine authchange queue invalidation, then independent functional nextgap: current CASE pipeline or NI01 receiving beautiful functional workspace. Mostlegacy alreadyexists: no second engine. Keepupdates≤60s/reports/screenshots. FilebackedUTF8builders; avoid JS interpolation in builder templates/Windows literalglob/PSstdinRussian/native:uid. Neverrerunoneshotbuilders.

"""+read(p)
print(json.dumps(files,ensure_ascii=True))
