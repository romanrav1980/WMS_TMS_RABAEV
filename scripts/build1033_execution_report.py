from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
page="""# NI03.3 — фактическое исполнение и действующее грузовое место

1015–1032 завершили связанный участок существующих экранов заказа и CASE. Проводки и исходные quantities не менялись.

## Что изменилось

Сводный статус явно различает превышение отбора, несогласованные единицы, закрытую недостачу, частичную недостачу, резерв и отмену. Отменённые строки не создают ожидание отбора; физический факт сохраняется отдельно. Отмена не скрывает превышение или проблему единиц. Статус PICKED считается по действующим строкам; количество отменённых строк видно.

Потребность и физический факт показывают свои единицы. Если перевод не согласован, количество заказа остаётся в исходной единице, отбор — в базовой; ложное обозначение обеих колонок одной единицей устранено. Резерв добавлен по каждой строке. Факт/остаток не складываются между разными SKU/UOM. Существующий отказ свыше2000строк сохранён — усечённый список не выдаётся за полный.

Таблица исполнения вынесена на широкую панель с точными количествами, причинами и счётчиками. Карточка заказа показывает деловые поля вместо JSON. URL order_id открывает конкретный заказ; выбор строки доступен клавиатурой. Смена заказа/пользователя/API и запоздавший ответ не заменяют текущую карточку/исполнение/доставку. Обработчики привязываются один раз.

Список комплектации перенесён из legacy-service в небольшой read-owner fulfillment: текущие RUSERS/право/WARE и источник проверяются до выдачи данных в одной READONLY транзакции. Прежние FACT_COMPOSITION_JSON/200facts/200SKU bounds и исторические поля сохранены. Убрано лишнее полное чтение деталей до проверки; API передаёт actor, missing404/denied403. Прямой get_fulfillment теперь требуетactor. Общий список/обычная карточка legacy заказов этим изменением не объявляются полностью scoped.

Дополнительно читаются CASE SSCC/текущая ячейка/версия. Текущая ссылка появляется только для активногоPICKED/размещённогоCASE с совпадающей привязкой версии. При несогласованном месте видно предупреждение; SHIPPED остаётся историческим фактом. Точные FACT_QTY/FACT_WEIGHT добавлены строками OracleTM9; прежние числовые поля сохранены для клиентов.

## Подтверждение

1017: адресная domain-проверка превышения, закрытой/смешанной недостачи, резерва, отменённых строк и раздельных единиц. Это логические случаи, не новые Oracleоперации.

Native1018/HTTP1020/browser24–25: существующий заказ1931 по исходной строке4EA имеет отбор3/остаток1/резерв0/активнуюстроку1. Источник не пересоздавался. 1024 проверил запоздавшие ответы двух заказов и смену пользователя.

Native1027/HTTP1031/browser26: сохранённый текущий заказ2133/CASE1131 показывает CASE10/FF10/12EA и ячейкуQI4bb85f1f15. Старый1931 содержит SHIPPED3 как историю без текущего места. Отказ существующему QA172_KRO подтверждён на уровне native scope; это не отдельное доказательство чужого склада, так как могли отсутствовать права. HTTPmissing404 подтверждён. Первая HTTPпопытка1031 пришлась до запускаAPI/ConnectError; после штатного старта повторный READ прошёл, никакая проводка не повторялась.

Architecture694/0cycles/76debt PASS после исправления новой аннотацииpublicfactory; широкий gate не повторялся. SQL1032: исходный bounded execution41.469ms/689.4buf; newfulfillment9.508ms/43buf (первыйвариантSQL). Решение fulfillment: сохранить bound2000/201/200 и ключи order/case; на большом заказе сгруппировать correlated facts/проверить план в отдельном ticket, владелец fulfillment. Новый индекс без объёмного плана не добавлять. Промышленная мощность не подтверждена.

ПолныйNI03.3 остаётсяin_progress: весь независимый/маркированный/оборудование/внешний объём не закрыт этими адресными изменениями. Задания Qwen подготовлены отдельно. Скриншоты24–26 и JSONсвидетельства находятся в этой папке.
"""
files["reports/nicora/2026-10-13/21-order-execution-report.md"]=page
files["reports/nicora/2026-10-13/21-order-execution-evidence.json"]=json.dumps({k:json.loads(read(p))for k,p in {"domain1017":"tmp/execution1017.json","native1018":"tmp/read1018_execution.json","http1020":"tmp/http1020_execution.json","native1027":"tmp/read1027_fulfillment.json","http1031":"tmp/http1031_fulfillment.json","sql1032":"tmp/sql1032_execution_read.json"}.items()},indent=2)
summary="1015–1033: orderstatus excess/closedshort/reserved/cancelled-active/UOM; currentactor readguards/deeplink/widepanel/reserve. Native1018/HTTP1020 old1931 picked3/remain1. Fulfillmentread1025/1026 scoped/currentREADONLY/originalfacts200/newCASE10FF10; native1027/HTTP1031/current2133/oldSHIPPED3/missing404. Architecture694/0/76PASS; report21/screens24–26. BoundedSQL41.469ms689buf/new9.508ms43 retainkeys; largerorder groupedbatch/plan ticket ownerfulfillment. FullNI03.3open."
files["wiki/components/nicora_order_execution_workspace_20261013.md"]="# NICORA — исполнение заказа и текущее место\n\n"+page
p="wiki/database/nicora_ni033_order_execution_20261013.md";files[p]=read(p)+"\n## Checkpoint1033\n\n"+summary+"\n"
p="wiki/index.md";files[p]="- [Checkpoint1033: исполнение заказа и текущий CASE](components/nicora_order_execution_workspace_20261013.md):current CASE10FF10/старый3+1/состояния/UOM/scopedfacts/report21/screens24–26.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint1033: "+summary+"\n"
p="wiki/requirements/nikora_delivery_v55/implementation_plan.json";v=json.loads(read(p));v["planRevision"]=43
next(x for x in v["increments"]if x["id"]=="NI03.3")["implementedSlices"].append(summary);files[p]=json.dumps(v,ensure_ascii=False,indent=2)
p="wiki/requirements/nikora_delivery_v55/implementation_plan.md";files[p]=read(p).replace("**Revision 42,","**Revision 43,")+"\nCheckpoint1033: статусы/UOM/резерв/широкийэкран/scopedfulfillment/currentCASE/readguard/deeplink. Original1931 3+1, current2133CASE10FF10; report21/screens24–26. ПолныйNI03.3 открыт.\n"
p="wiki/requirements/nikora_delivery_v55/execution/active/ni03_3.md";files[p]=read(p)+"\n1015–1033: сводныйstatus/UOM/reserve/currentordercontext и scopedcurrent fulfillment/originalfacts/currentCASE10FF10. Original1931 picked3/remain1/current2133CASE12, native/HTTP/JS/browser; [отчёт21](../../../../../reports/nicora/2026-10-13/21-order-execution-report.md). Statusin_progress сохранён.\n"
p="reports/nicora/2026-10-13/index.html";files[p]=read(p).replace("</main>",'<article><h2>21 · Исполнение заказа и текущий CASE</h2><a href="21-order-execution-report.md">Отчёт №21</a><p>Резерв, точные единицы, недостача, текущая версия CASE и история отгрузки.</p><a href="screenshots/25-order-execution-panel.png">Исполнение</a> · <a href="screenshots/26-order-current-case.png">Текущий CASE</a></article></main>')
p="wiki/runbooks/nicora_active_work.md";files[p]="# Актуальный checkpoint1033,13.10.2026 около19:32MSK\n\nРаботать до20:00MSK=17:00UTC либо фактическогоall; ещё28минут. Plan43/currentNI03.3, все18неполностьюготовы/Githubнепубликоватьдоусловия. Ниже старые записи исторические.\n\n"+read(p)+"\n## Checkpoint1033\n"+summary+"\nCurrent API1030(rootserv) newscopedget_fulfill, actualHTTP1031passafterinitialconnectrace. CustomerOrderService.get_fulfillment now requiresactor; soleproductioncallerrouterupdated; old factories notrerun. Newownerorder_fulfillment_read.py sharednativeScope/readONLY/oldJSONbounds/newCASEjoin/currentCASE flag/exactfactstrings. Initial1025ASTdedent failedSQLreplace+untypedfactory;1026fixedbeforelive tests, architecturePASS694. Formatting1028noSQLsemanticchange/newcursor possible,1032onlyfirstversionmetrics. UI1021scopedresponsegeneration/resetdelivery/context/auth/bindonce/deeplink,1022metadata,1023wideexecution,1028currentCASE link. Native1018old1931read3+1/HTTP1020; domain1017logicnotDBbirth; JS1024races. Source1002 retainedP20H20 unchanged, currentCASE1131ver10 slot224/QI/root8slot222. BrowsercaseTargetcurrent2133?v1028/screens26,reportFs; screenshots24–26actual. QwenNI03.3tasks added. Encodingafterlatestdocs stillneeded; no fullgate/broadtest/copy/agents/commit/push. Nextonlybounded functional ticket canfitbefore17UTC, retainwork/checkpoint andactualclock.\n"
qroot=list(Path(".").glob("*/NI01.1"))[0].parent
files[str(qroot/"NI03.3"/"21-order-status-UOM-current-CASE.md")]="""# Qwen: исполнение заказа
Не запускать старые фабрики. Report21: read-only1931 picked3/remain1 и2133 CASE1131 12EA/version10/FF10/QI/slot224. Отгруженныйфактнеобъявлятьтекущимзапасом.
Свой domain/Oraclecase: превышение→OVER_PICKED, закрытаяshort→SHORT_CLOSED, short+незавершённые→PARTIAL_REFUSED, резервбезфакта→RESERVED, canceled строки неpending, canceledexcess не скрывать. Несогласованнаяконверсия сохраняет единицыпотребности и фактараздельно; никакогосуммированияразныхSKU/UOM.
get_fulfillment требуетactor; currentRUSERS/WARE/rights/scopedread/200facts/200compositions/2000executionlines. Проверить actualforeignWARE отдельно от no-rights; missing404/currentCASEversionstalewarning/SHIPPEDhistory. Race oldorder/oldactor/API/duplicatebindings/deeplink/keyboard. Скриншоты/SQLрешение; непроверенное неPASS.
"""
print(json.dumps(files,ensure_ascii=True))
