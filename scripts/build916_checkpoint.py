from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8")
files={}
page="""# NI01.1: позиции SAP и рабочая приёмка

Checkpoint916, 13 октября.905 APPLIED, RABAEV/orcl; capture904/SHA/paired rollback. Version2 предполагаемого WarehouseSupplyOrder поддерживает разные LineNumber одного SKU, version1 сохраняет запрет. Это формат шлюза, не стандартный SAP IDoc; ARTMAS10 не меняется. WMS-профили маркировки сохраняются.

Source PK(order,line) сохранён, прежние UNIQUE ROW_ID и order/articul заменены lookup indexes. Legacy RRL_PRIHOD_NAKLAD_ROWS UNIQUE(document,articul) сохранён: одна каноническая строка с точной суммой планов BASE. SupplyLineWriter выделен из фасада, записывает только исходный план. Native Receipt CORE/PLAN уже работают по order/line, stockroot unchanged ACTIVE/compatOFF. Detail/quantity amendment/header completeness используют original POSTED_BASE_QTY/STOCK_BASE_UOM по order/line; неправильная baseline запрещена. Принятую строку нельзя удалить/уменьшить ниже факта. Shared legacy row удаляется лишь без ссылок.

DDL инвалидировал9 зависимостей; 003_compile восстановил их,907 USER_ERRORS[]/INVALID[]. Полного копирования БД нет. Rollback отказывается при уже существующих v2 shared rows, не удаляет данные; rollback не испытан.

Actual908: планы3+3, первая приёмка3 physical units/6codes CRPT/TOBACCO и EGAIS/ALCOHOL, первая accepted3/remaining0, вторая accepted0/remaining3. Cached root repeat/layout3, own reversalP/H0, protected688 stock/version unchanged. Actual910 такой же baseline; resume911 на сохранённом source910: revision2 canonical7(line3+4), accepted shrink3→2 refused atomically, revision3 delete unreceived line/canonical3 retained. Затем native own reversalP/H0.

Непрошедшие попытки:900 v1 rejected422 до данных;906 stale API v1 rejectedv2, rootserv.bat907 restarted hidden;909 amendment reversed908 correctly refused. Initial910 harness ошибочно загрузил ctx908, amendment и повторное сторно908 refused; resume911 использовал правильный сохранённый910 без новой товарной приёмки. Эти попытки не PASS; чужой запас не изменён.

Receiving894/912/915: responsive source/orders/lines/pallet, deep source link, current WMS profiles, busyfieldset/stale guard, кнопки выбора/keyboard/highlight, zero-remaining guard. Source detail содержит native incoming condition/receipt_allowed/state OPEN/COMPLETE/REVERSED/RECONCILED; closed source blocks new UI-confirm, reversed counts исторические. Browser896 protected688 auto-singleline/profile2/confirmdisabled screenshot14. Browser908 two-line counters screenshot15. Manual CUA selections не дали наблюдаемого результата, не сертифицированы; Playwright connector navigate hung/terminated, не PASS. Последний915 status browser ожидает.

SQL914: detail3.678ms/32buffers, canonical2.236ms/38, received0.765ms/18.13, completeness3.234ms/17.75. Retain <=1000 source lines/indexed order-line receipts (existing RRL_SAP_RECEIPT_LINE_IX)/canonical legacy key; no extra stock index/writer. Не промышленная нагрузочная приёмка.

Architecture691/0cycles/76 allowances PASS tightened down; Node receiving/context syntaxPASS. Encoding run21783 pending. NI01.1 full realSAP/ACK/concurrency/hardware/independent gates остаются; all18 not complete. Plan36/currentNI03.3, continue until20:00MSK13Oct2026. GitHub не публиковался.

[SQL](../../db/migrations/2026-10-13_ni011_supply_line_v2/apply.sql).
"""
files["wiki/database/nicora_ni011_supply_lines_20261013.md"]=page
files["reports/nicora/2026-10-13/13-sap-receiving-report.md"]=page+"\n[Screenshot14](screenshots/14-sap-receiving-workspace.png) · [Screenshot15](screenshots/15-sap-two-lines-workspace.png).\n"
files["reports/nicora/2026-10-13/13-sap-receiving-evidence.json"]=json.dumps({"908":json.loads(read("tmp/context908.json")),"910_911":json.loads(read("tmp/context910.json")),"slow914":json.loads(read("tmp/slow914.json")),"independent_acceptance":False,"manual_browser_selection_passed":False},indent=2)
p="db/migrations/2026-10-13_ni011_supply_line_v2/apply.sql";files[p]="@@001_lines.sql\n@@003_compile.sql\n@@002_ledger.sql\n"
p="db/migrations/2026-10-13_ni011_supply_line_v2/rollback.sql";files[p]=read(p).replace("update RRL_SCHEMA_MIGRATIONS","@@003_compile.sql\nupdate RRL_SCHEMA_MIGRATIONS")
p="db/migrations/2026-10-13_ni011_supply_line_v2/checkpoint.json";obj=json.loads(read(p));obj["state"]="APPLIED_DEV_VALID";obj["evidence"]="908/910/resume911;907 errors[]/invalid[]";obj["current_control_sha256"]={x:hashlib.sha256(y.encode()).hexdigest()for x,y in files.items()if x.startswith("db/")};files[p]=json.dumps(obj,indent=2)
p="reports/nicora/2026-10-13/index.html";files[p]=read(p).replace("</main>",'<article><h2>13 · Приёмка и позиции SAP</h2><a href="13-sap-receiving-report.md">Отчёт №13</a><p><a href="screenshots/14-sap-receiving-workspace.png">Приёмка</a> · <a href="screenshots/15-sap-two-lines-workspace.png">Две позиции</a></p></article></main>')
p="wiki/requirements/nikora_delivery_v55/implementation_plan.json";plan=json.loads(read(p));plan["planRevision"]=36;inc=next(x for x in plan["increments"]if x["id"]=="NI01.1");inc["implementedSlices"].append("894-916 receipt workspace/current profiles, explicit v2 per-item/shared legacy SKU, posted-base progress; actual908/910/resume911 receipt/amend/reversal, UI manual/external gates remain");files[p]=json.dumps(plan,ensure_ascii=False,indent=2)
p="wiki/requirements/nikora_delivery_v55/implementation_plan.md";files[p]=read(p).replace("**Revision 34,","**Revision 36,").replace("**Текущий — [NI03.2](execution/active/ni03_2.md)","**Текущий — [NI03.3](execution/active/ni03_3.md)")+"\nCheckpoint916: NI01.1 per-item gatewayv2/shared canonical legacy row/current receipt UI, actual908/911; all18 остаются незавершёнными. [[database/nicora_ni011_supply_lines_20261013]].\n"
p="wiki/requirements/nikora_delivery_v55/execution/active/ni01_1.md";files[p]=read(p)+"\n894–916: gatewayv2 separateitem/shared canonicalrow, postedledger, receivingworkspace/currentstates. Actual908 marked3/6codes, resume911 amendments7→3/shrinkdenied/ownreverse; manual browser and external remain. [[database/nicora_ni011_supply_lines_20261013]].\n"
p="wiki/index.md";files[p]="- [Checkpoint916: SAP receiving](database/nicora_ni011_supply_lines_20261013.md):905 VALID/908+911 perline+amend+reversal, report13/screenshots14–15, plan36/manual UI pending.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint916:905v2 source lines/shared unchanged legacySKU row APPLIED/907 VALID; actual908/910 markedreceipt3/6codes, resume911 amend7→3/shrinkdenied, ownP/H0. Failed900/906/909/initial910 distinguished. SQL914 bounded existingorderlineindex. Receiving894–915/currentprofile/source-state; manualCUA notpassed. Report13/screenshots14–15/plan36/currentNI03.3/all18notdone. Arch691/0/76 tighteneddown, encoding21783pending.\n"
p="wiki/runbooks/nicora_active_work.md";files[p]="""## Checkpoint916 — 13Oct2026 15:03MSK

USER deadline20:00MSK17:00UTC OR allactualcomplete, doNOTfinal/stop before. Plan36/currentNI03.3/full17remain, conditional fullcommit/GitHub AFTERALL, excludeSAP. No agents/copies.

905v2 source metadataAPPLIED/9dependencies compile907VALID; RootACTIVE/compatOFF unchanged. Explicitgatewayv2 duplicateSKU distinctline/share canonicallegacyrow, v1dupnegative. NewSupplyLineWriter planneronly/perlinePOSTEDledger/detail/amend/header. Actual908 first3/3keys6codes second0/remain3; ownreverseP/H0/protected688 unchanged. Actual910samepositive; initialharnessloadedctx908 beforeamend/cleanupandbothrefusedclosed; resume911 correctsaved910 rev2canonical7, shrink3→2 refused, rev3deleteunreceived/canonical3, nativeownreverseP/H0. NEVERrerun900/906/908/910factories/909/911initial. Context908 historical2lines/source3aa116e51983443e8b20d055195a22b8, context910revision3singleline; bothREVERSED3.

UI894/912/915 responsivecontext/profiles/buttons/keyboard/busy/stale/closedsource; detail915join incomingcondition/receipt_allowed/status, historicalreversedaccepted. Browser896auto688actual/screenshot14;908two-line screenshot15before915. CUAmanualrow/buttonclickreturnedNOobservableeffect, NOTpassed; alternatePlaywrightconnectornavigatehung/terminated9012. Avoidendlessclicks; appvsautomationcauseunsettled. CUA taskTab821857734/browser2/reportFs current908URL8088/wms-admin/receiving.html?supply_order_id=3aa116e51983443e8b20d055195a22b8; taskTab.click direct, notcua.click; latest915reloadpending. No browserinjection/networkevaluate.

serv.bat907APIv2live; session42466 helperstillrunningmaypoll; encoding21783stillrunningPOLLatnext. Arch691/0/76tighteneddown/NodechecksPASS. SQL914 detail3.678ms32buf/row2.236ms38/received.765ms18/header3.234ms17.75, retainbounded1000/existingorderlineindex. Migration apply/rollback includes003compile916, don'tfullreapply. Reports01–13/screenshots01–15; report13JSONcopied908910contexts. Latest915state/currentreadproofpending. Extraafter893 waveauthchangequeueclear/reload andheadertrueORDER_COUNT/TASK_COUNTcodeedited, newcounterSQLdecisionpending.

Protected688P3H3/CASE1031/1032P20H20/money107.25current0 unchanged. Native852866869872877 existingcaseproofs earlier893 below. Nextmanualreceiving correctcause/current915browser thenNI03.3 fullCASE/control/shipping/marked topologyfunctionalremaining. ExternalNI02auto-splitchoice/actualGovcountriesendpoints/certs unanswered; nofakeACK. 80%functionality, targetedtestsonly. Use observedpaths/UTF8writer, PSStop+LASTEXITCODEguard; no rerunoneshot builders, no nestedtriples/JSbackticktext/native:uid mistakes.

"""+read(p)
dirs=list(Path(".").glob("*/NI01.1"));assert len(dirs)==1
files[str(dirs[0]/"916_supply_lines_v2.md")]="""# Qwen — NI01.1 per-item SAP receipt

Independent review: wiki/database/nicora_ni011_supply_lines_20261013.md and supply_line_writer/amendments/reads, original nativeReceipt CORE/PLAN. Newownfixture only: v2twoitemlines3+3sameSKU, firstreceipt3/physical3keys6codes notdoubleP, secondaccepted0, exactreplay/conflictingpayload; canonicallegacyrow6. Amendment/unreceiveddelete retainscanonical; receivedshrink/deletion refused; v1dupSKU/v2dupLine reject. Race sourceversion/receipt mustnotpartialplan/stock.

Saved908/910 REVERSED, neverfactories/rebirth; protected688 andCASE1031/1032 read-only. Ownnewfixture cleanup viaRootreversal only, no disablingguard/copies. UI actualmanualbuttons/keyboard/currentprofiles/late-response/busy/currentclosedstate: CUA manual selection currently UNPROVED, inspectconsole/network separately. Save screenshots/actionreport approved reports/nicora/2026-10-13. Distinguish ownindependent vs author908/911; slowSQL decisionbounded, no broadload/externalACKfiction.
"""
print(json.dumps(files,ensure_ascii=True))
