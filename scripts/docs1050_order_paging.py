from pathlib import Path
import json
files={}
report="""# 24 · Переход к старым заказам

13.10.2026. NI03.3, существующий reader/customer-orders UI.

Добавлены keyset before_id, «Старее/Новее», сброс страницы при фильтре/новой сессии, текущий actor/API guard. Во время загрузки старые строки очищаются; ошибка не выдаёт старую страницу за новую. Сохраняется выбранная карточка заказа.

SQL теперь выбирает до500 header по текущемуWARE/фильтрам/ID до соединения с row и подсчёта итогов. Сортировка IDdesc, исходные агрегаты/поля сохранились. Для legacy отрицательных ключей (-980711 DS-BASE-O1 и далее) сохранены чтение карточки, URL и cursor. Нулевойcursor422; detail0 остаётся409. Первое предположение проверки «before1 пусто» было неверным из-за этих старых строк; исправлен сценарий с конкретным фильтром, данные не удалялись.

Native1046: соседние3+3безпересечений, возврат на первую, filtered2134→2133, отрицательный legacy key/следующаястраница, пустой filteredtail/invalid — PASS. HTTP1049: actualpages/admin/negative200/invalid422 — PASS. JS1048: paging/filter reset/error no stale/newactor — PASS после исправления mock innerHTML setter (реальный DOM исходно очищает children). Скриншот30 — настоящий список/кнопки/currentCASE12/CTFF10; ручной CUA click перехода не заявляется.

SQL1046 новый ограниченный list11.060–19.280ms/28–45.5buf; старая форма16.421ms/50.7buf на малом наборе. Это не доказательство производственного ускорения. Решение fulfillment: сохранять headerbound500/keyset и существующие ключи; для больших объёмов проверить планы поиска LIKE/status/WARE и статистику, индекс только по фактам. Stock/P/H/codes/history неизменны.

Gate1044: architecture695/0cycles/76debt, 24 architecture/tooling tests, оба TypeScript typecheck — PASS, pytest cache warning. Architecture после1048 — PASS. Encoding check перед документами1044 прошёл; окончательный после последних документов выполняется отдельно. Все18 спринтов не закрыты.
"""
files["reports/retailcase/2026-10-13/24-order-paging-report.md"]=report
files["reports/retailcase/2026-10-13/24-order-paging-evidence.json"]=json.dumps({"native":json.loads(Path("tmp/read1046_order_paging.json").read_text(encoding="utf-8")),"http":json.loads(Path("tmp/http1049_order_paging.json").read_text(encoding="utf-8"))},indent=2,ensure_ascii=False)
p="reports/retailcase/2026-10-13/index.html"
files[p]=Path(p).read_text(encoding="utf-8").replace("</main>",'<article><h2>24 · Старые заказы и ограниченная выборка</h2><p>Переход между страницами, фильтры, старые внутренние ID; ограничение документов до расчёта итогов.</p><a href="24-order-paging-report.md">Отчёт</a><img src="screenshots/30-order-keyset-pages.png" alt="Список заказов с переходом Старее и Новее"></article></main>')
p="wiki/components/retailcase_order_execution_workspace_20261013.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n## Пагинация1045–1050\n\n"+report.split("\n\n",2)[2]
for p,note in [
("wiki/index.md","- [Пагинация1050](components/retailcase_order_execution_workspace_20261013.md): scoped headerbound/keyset/negativelegacy/24report/30screen, NI03.3 in_progress.\n"),
("wiki/log.md","\n- 13.10.2026 checkpoint1050: header-first list/keyset UI, actualnative/HTTP/JS, negativelegacy keys retained; report24/screen30. Gate1044 PASS, currentarchitecturePASS; next nested waiting existingHU caller analysis.\n"),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni03_3.md","\n1045–1050 original order list headerbound/keyset/UI pagination/legacy negative keys, report24/screen30; no stock writes/full closure.\n")]:
 t=Path(p).read_text(encoding="utf-8");files[p]=note+t if p.endswith("index.md") else t+note
p="wiki/runbooks/retailcase_active_work.md"
files[p]="# Checkpoint1050 — непрерывное исполнение\n\nВладелец велел выполнять до фактического завершения, прежний20:00 отменён. Все18 не закрыты, GitHub only afteractualall. API1048 includes originalorder scoped/exact/headerbound/keyset/negativelegacy keys; report23–24/screens29–30. Fullgate1044PASS24/bothTS/arch6950/76; latearch1048PASS, Nodepaging1048PASS aftermockfix/native1046/HTTP1049PASS. No newstock. Next: NI07.2 nested-HU waiting GAP, reuseexistingHU tasks; capturefreshcurrent sources beforeDDL, inspectdefer/WAIT physical/HUplan root. Existingretained1002P20H20/CASE1131FF10+CASE1132FF6/ownHU7/currentQI unchanged; neverrerunfactories. BrowsercurrentnewownChrome2tab821857750 order1043Tab/orderReportFs1043; prior alloldtabsclosed. No agent/goal.\n\n"+Path(p).read_text(encoding="utf-8")
files["задания на проведения тестов/NI03.3/1050_страницы_заказов.md"]="Проверить before_id/новее/старее, nonadmin currentWAREfilter доlimit, фильтры междустраницами, lateactor/no stale/error; негативные legacy IDs не удалять. Сохранённые1931/2133 и DS-BASE-O1 read-only. Нет фабрик/реальныхSAP/stockwrites. SQLheaderbound500 и actual plan не заменяются фальшивым productionclaim. Report24 evidence, независимая приёмка отдельно.\n"
print(json.dumps(files,ensure_ascii=True))
