from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8")
files={}
page="""# NI03.3: исполнение заказа в одном текущем снимке

922/925 APPLIED, RABAEV/orcl, USER_ERRORS[]/INVALID[]. Existing OrderExecution не меняет товар: прежние CASE/FULLPAL факты и exact base units, bounded2000 lines сохранены. Теперь get(order,actor) читает WARE/permission/header/physical rows в одной READ ONLY transaction. Native existing RRL_STORE_ORDER_SCOPE.assert_scope расширен только read whitelist customer_fulfillment_view. Active RUSERS/current WARE/GLOBAL_ADMIN/current right; begin_source/write whitelist и quantity writer не изменены. Source924/SHA/paired rollback; rollback не испытан. Первый923 на прежнем whitelist отказалadmin, неPASS.

API передаёт username/map403; добавлены warehouse_id/consistent_snapshot при сохранении старогоJSON. UI generation/actor/API/current order guards не позволяют позднему ответу старого запроса заменить свежие физические строки. При смене auth старые цифры очищаются; понятные статусы. ПодготовленнаяСТ не означает PICKED.

Actual923 admin order1930/WARE20052672 PENDING в одномснимке, missingviewer и QA172_KRO без fulfillment-right отказали до quantity query. У QA172_KRO тот жеWARE и right0: это отказпо праву, НЕ доказательство foreign-warehouse denial. Nonadmin own/foreign with validright остаются отдельной проверкой. Actual929 retained172 order1929 SHIPPED3 → PICKED3/remain0; retained173 same originalorder1931 qty4 → PARTIAL picked3/remain1. Исторические фабрики и запас не изменены. HTTP926 после штатногоrestart927: consistent_snapshottrue/currentWARE/statusPENDING. JS928 newer same-order response wins/authclear/no writes.

SQL926 physical progress69.478ms/1078buffers(3exec). Решение fulfillment owner: сохранить bounded2000/order keys; для больших заказов backlog grouped batching/план/stats, не добавлять speculativeindex. Не промышленная приёмка. API StatReload фактически не подхватывает код, штатныйserv.bat требует доступа внепесочницы для остановки старогоPID.920/927 разрешённые скрытые рестарты успешнообновилиHTTP. Исправлениеwatcher как отдельный operational gap.

Receiving930: cached success проверяет OP/line/pallet/exactquantity/status/task до удаления durableintent; повреждённыйответ/изменение другойвкладки сохраняют исходныйзапрос. Retry после confirmedresponse перечитывает original source дажеприbusy и блокируетfieldset. JS917/931 PASS. HTTP932 original908 receipt cacheexact после reverse; HTTP933 original910 cacheexact после SAP revision3 иreverse; ownP/H0/версииunchanged, currentsourceREVERSED/newreceiptfalse. Это историческийответ, не новый stockbirth. Browsermanual после сбоя расширения остаётся непроверенным; falsePASS нет.

Quality919 PASS24/bothTS/arch6910cycles76; cachepermissionswarning. Encoding21783PASS (до позднихrawUI/doc изменений). Node922930931 PASS. All18 notdone, NI03.3 fullmarked/terminal/independent residuals open, GitHub не публиковался. До20:00MSK продолжается функция.

[SQL](../../db/migrations/2026-10-13_ni033_order_execution_scope/apply.sql) · [SAP source](nicora_ni011_supply_lines_20261013.md).
"""
files["wiki/database/nicora_ni033_order_execution_20261013.md"]=page
files["reports/nicora/2026-10-13/14-order-execution-report.md"]=page
files["reports/nicora/2026-10-13/14-order-execution-evidence.json"]=json.dumps({"order923":json.loads(read("tmp/order923.json")),"retained929":json.loads(read("tmp/order929.json")),"http_sql926":json.loads(read("tmp/execution926.json")),"receipt932":json.loads(read("tmp/recovery932.json")),"receipt933":json.loads(read("tmp/recovery933.json")),"independent_acceptance":False,"browser_manual_passed":False},indent=2)
p="db/migrations/2026-10-13_ni033_order_execution_scope/checkpoint.json";v=json.loads(read(p));v["state"]="APPLIED_DEV_VALID";v["evidence"]="923/929 readonly currentfacts,926 HTTP,928 JS; no stock changes";files[p]=json.dumps(v,indent=2)
p="reports/nicora/2026-10-13/index.html";files[p]=read(p).replace("</main>",'<article><h2>14 · Фактическое исполнение заказа</h2><a href="14-order-execution-report.md">Отчёт №14</a><p>Один снимок Oracle, текущие права и защита поздних ответов.</p></article></main>')
p="wiki/requirements/nikora_delivery_v55/implementation_plan.json";v=json.loads(read(p));v["planRevision"]=37
inc=next(x for x in v["increments"]if x["id"]=="NI03.3");inc["implementedSlices"].append("922-934 current native fulfillment read scope/single readonly header+physical facts, old173 order4 physicallypicked3/remain1; HTTP926/currentWARE/JS928 stale response; no new stock writer")
inc=next(x for x in v["increments"]if x["id"]=="NI01.1");inc["implementedSlices"].append("930-933 exact receipt-response correlation/scoped durable settlement/originalsource retry refresh; actual cached908 and amended910 after reversal no stock rebirth; manual browser remains open")
files[p]=json.dumps(v,ensure_ascii=False,indent=2)
p="wiki/requirements/nikora_delivery_v55/implementation_plan.md";files[p]=read(p).replace("**Revision 36,","**Revision 37,")+"\nCheckpoint934: NI03.3 execution current scope/single snapshot и NI01.1 exact receipt recovery, report14; старые172/173 read-only3/remain0 и3/remain1, источникнепересоздавался. [[database/nicora_ni033_order_execution_20261013]].\n"
p="wiki/requirements/nikora_delivery_v55/execution/active/ni03_3.md";files[p]=read(p)+"\n922–934 current order fulfillment snapshot/native scope/API/UI, actual923/929/HTTP926+JS928. Original173 order4 picked3/remain1 confirmedreadonly. [[database/nicora_ni033_order_execution_20261013]]. Fullmarked/independent lifecycle remains.\n"
p="wiki/index.md";files[p]="- [Checkpoint934: исполнение заказа](database/nicora_ni033_order_execution_20261013.md):925 VALID/current snapshot, original3/0 и3/1/HTTP926, receipt930–933 recovery; report14/plan37, browser unavailable.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint934:922/925 native fulfillment view whitelist/current scope/single readonly snapshot APPLIED/VALID; actual923 missingright denial (sameWARE, not foreignproof), retained929 orders1929picked3remain0/1931picked3remain1; HTTP926 currentafter927, JS928 staleguard. SQL69.478ms1078buf retainbounded2000; largeorderbatching ownedfulfillment backlog. Receiving930 correlateddurable/retrybusyrefresh; JS931/HTTP932933 cache afterreversal/amend no rebirth/versionsunchanged. Quality919PASS/encoding21783PASS earlier; browserextensionunavailable. Report14/plan37/all18notcomplete. Activeworkoldhistory archived tokeepcurrentpage small.\n"
p="wiki/runbooks/nicora_active_work.md";files["wiki/runbooks/archive/nicora_active_work_before_934.md"]=read(p)
files[p]="""# NICORA — текущая работа, checkpoint934

13.10.2026, около15:25MSK. USER: непрерывно до20:00MSK (17:00UTC) либо фактического завершения всех18. Не завершатьturn/status-only раньше. Plan37/currentNI03.3, толькоNI03.1 devcomplete, остальные17 полных открыты. Fullcommit/GitHub поручены толькоПОСЛЕВСЕХ, SAP/SAP_INTEGRATION исключены. Пока публикации нет. No agents/goals/copies, >=80%functionality.

## Среда и последние изменения
RABAEV@127.0.0.1:1521/orcl; единственный RRL_STOCK_POSTING_API ACTIVE/compatOFF. Native925 APPLIED/VALID, добавляет только existing RRL_STORE_ORDER_SCOPE actor_scope READ whitelist customer_fulfillment_view. Begin_source/writes unchanged. Capture924/SHA/pairedrollback/ledger. OrderExecution.get теперьтребуетactor и читает WARE/currentnativepermission/header/physical rows в одной READONLY transaction; APIusername/map403, UI stalegeneration/actor/APIguard. ExistingCASE/FULLPALquantityqueries bounded2000 unchanged. Actual923adminorder1930PENDING; QA172_KROsameWAREright0 denied, НЕ foreign-warehouse proof. Actual929 oldsource172order1929SHIPPED3 →PICKED3/remain0; source173sameoriginalorder1931qty4→PARTIAL3/remain1. No stock/source factories.

Native905 supplyv2APPLIED/9dependencies compiled907VALID. Version1 rejectsduplicateMaterial; explicitgatewayv2 permitsdistinctLineNumber sameSKU/shared onecanonicallegacy document/SKU row sumBASE. Originallegacy UNIQUE remains. NewSupplyLineWriter planner-only. Detail/amend/headercompleteness use originalPOSTED_BASE_QTY/STOCK_UOMperline. Actual908 line3+3 first3/3physicalkeys6codes second0/remain3/replay/layout; ownreverseP/H0/protected688unchanged. Source910samebaseline thencorrectresume911 amendedrev2canonical7, shrinkaccepted3→2 refused, rev3deleteunreceived/sharedcanonical3 retained; ownreverseP/H0. Initial910harness wrongly loadedctx908 beforeamend/cleanup, bothclosedguardsrefused; recordednotPASS.900v1/906staleAPI/909alreadyreversed negativesnotPASS. NEVERrerun900/906/908/910factories/909/911initial.

Receipt930 correlated success OP/line/pallet/exactquantity/RECEIVED/taskID beforedurableintent removal; changed-other-tab body/malformed2xx retained. Retry usesconfirmedRefresh=true despitebusy +fieldsetdisabled. JS931/917PASS; HTTP932 old908 cachedreceipt exactafterreverse;933 old910 cachedexact afterrev3+reverse, sourceREVERSED/newreceiptfalse/ownP-H0/versionsunchanged. Cache responsehistorical, notnewstockbirth. Saved908 order3aa116e51983443e8b20d055195a22b8 still2lines;910revision3singleline; bothREVERSED.

## Runtime/evidence
LocalAPI8088, rawUI /wms-admin/, React3000 (not8089). StatReloadcurrentlydoesNOTpick upchanges. Rootserv.bat sandboxkill fails; require_escalated Start-Process rootserv.bat WindowStyleHidden withtmpout/errlog approved920/927 andactualnewHTTP. Restartonceaftercompletedticket; don'tassumehotreload. Current927 servercurrent922. Metadatachangesneed no restart. Roothelpers42466/95462 likelycomplete; no needpoll unless reportedrunning. Encoding21783 finalPASS. Gate91924/bothTS/arch6910cycles76PASS cachepermissionswarning. Later922archPASS/Node928930931PASS. Newdocencodingpending.

SQL914 receivingdetail3.678ms32buf/canonical2.236ms38/received.765ms18/header3.234ms17.75, retainbounded1000/existingorderlineindex. SQL926 oldphysicalprogress69.478ms1078buf3exec; retainbounded2000/orderkeys, ownerfulfillment largerordergroupedbatch/planbacklog; nofakeproductionload. Report14has926currentJSON copied. VSQLSQL_TEXTlimited1000: filterqueryprefix, notaliasesafter1000chars.

Reports01–14/screenshots01–15 approved C:/projects/TMS/reports/nicora/2026-10-13. Screenshot14 realprotected688 currentprofile/auto-singleline/confirmdisabled;15two-line908 before915status. Browser manualrow/buttons gaveNOobservableeffect, notcertified; JS917 actualcontroller handlers work. CUAafterreset getTab/tabs.get/claimTab fail debuggerconnection; summarise as browsercontrol unavailable through extension. Alternate tms_playwrightnavigate hungterminated9012. No moreblindclicks/installations/networkinjections. CUA runtime has taskBrowser selectedChrome2/nameSession, taskCandidate current908 tab butNOtaskTab binding duefailedattach; browseruserown tabsunrelated ignored.

## Prior critical deliveries/protected sources
852sharedcapacity onephysicalincoming;866same-sourcebindings;869owneraggregate;872exacttarget/allownincoming;877currentpickscope before replay/afterlocks: APPLIEDVALID. Fresh867wave546/task1099DONE20 own12/other8 no next, owncleaned; related850wave547whole20+12 owners12/8/14cleaned.879wave551/task1104 existingCasePickServicehelper thenrelease/servicecache/foreignQA172scope/replaycleaned; don'tusefirstdirectnativebody OP againstservicebody. Reports10/11 JSON savedauthoritative.

UI860–893 execution/view/sharedcommandintent with PICK/FINISH keyprefix validators, exactcorrelation/currentauth/recovery, threepanels. WaveQueueReads wrapsoldreaders/currentnativewarehouse/READONLY, leanheader avoidscomposition; headerrealORDER_COUNT/TASK_COUNT after893 edited, newcounterSQLcheckpending. PickeroldTMS dates/district/store implemented791–812, nosecondassignmentengine. WHTqueue2filters/exactquantity deep1080 done. FullNI03.2weighted/marked/concurrency andNI03.3marked/nested/multi-place/independent open. NI07.2CASE/sharedCFG4/dayclose andNI02splitchoice/Govactualendpoints/certs unanswered; nofakeexternalACK.

Protected: task1080/SAP688 UID LEGACY.SAP.688:e0ef17c2c03b427b9c5fc58d852c71a3 currentlyP3H3/3physicalkeys6codes/Ware6524567, oldFFpicked3; NEVERfactories669–673/688/744/745/773/cleanup. CASE1031/1032P20H20/Ware6667491; oldmoney107.25/current0. Group671/717history alreadydeliveredP0, norebirth. New867/879/850/908/910 ownP/H0, noinitialcase reruns.

## Next work
Continue independentfunctionalremainingNI03.3/NI04/otherplans untildeadline; nofinal early. Current fixesfunctional; fullindependent/realERP/hardware notclaimed. Couldcontinue receiving damagedintent recovery/userfunctionalcontrol or existing fullmarked CASE lifecycle gaps, reuseowners andcurrentRoot. Docs/gatesdurablecheckpoint essential butkeepresourcefocusfunctionality. No broadtests/DBcopies/Qwenruns.

Use exactobserved paths via rg --files before reads; PS UTF8, Pythonread/write encodingutf8, JSONstdoutensure_asciiTrue (consolecp1251 can'tprintarrows). Storewriter in functions: eval("("+load("writeStockFiles")+")"). File-backedbuilders emitJSON; PS ErrorActionStop +LASTEXITCODEcheck before applying. Don'trerunoneshotbuilders; reapplysavedJSON ifwritefailed. OuterJSbacktick mustNOTcontain literalbacktick/$interpolation; nestedPythontriplequotes requirecare. Native SQLbind :p_uid (not:uid), reset_connectionaftercommit/rollback. tools.session_id→write_stdin, functions.cell_id→wait; no>60swaits. No agents bydeveloper.

[Previous detailed context archive](archive/nicora_active_work_before_934.md) retains earlier source identities and history.
"""
dirs=list(Path(".").glob("*/NI01.1"));assert len(dirs)==1
files[str(dirs[0].parent/"NI03.3"/"934_order_execution_read.md")]="""# Qwen — current order execution

Review925 scope whitelist read-only,922 header+facts oneREADONLY snapshot/currentactive rightsWARE; exactoldquantity logic retained. Actualscopepositiveadmin, missingrightnegative proved; nonadminvalid-right own/foreign separate independentcase. APIactor403, no missingrights fallback. UI sameorder delayed oldresponse/authchange clear.

Oldretained172/173 sources arehistorical/read-only; no factories. Expectorder1929picked3remain0 and1931order4picked3remain1. Protected688/CASE1031/1032 untouched. For freshCASE/FULLPAL positive use ownfixture+existingRoot. Save report/screenshots approvedreports. CheckslowSQL batchingplanbound2000/production evidence notclaimed.

Receipt930 cachedsettlement verifiesOP/line/UID/quantity/status/task; wrongsuccess keptpending. Retry refresh afterbusy; old908/910 reversed cachedresponses doNOTrebirth. Browsercontrolunavailable, manualUI notpassed. Independentconsole/network/browserselection needed whenextensionworks. Do notclaimauthorJS917928931 isindependentacceptance.
"""
print(json.dumps(files,ensure_ascii=True))
