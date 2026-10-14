from pathlib import Path
import json
out={};page="wiki/database/nicora_ni061_shortage_reconciliation_20261011.md"
out[page]="""# Сверка недостающего межскладского товара
294: существующая частичная291/292 приёмка остаётся единственной проводкой. GET /api/inventory/interwarehouse/receipts/{receipt}/shortage читает один READ ONLY snapshot: текущий RUSERS/right/склад одного плеча, APPLIED receipt, frozen original+accepted units, original load custody и текущие единицы/число зарегистрированных кодов.

Для обычного товара показывает исходное3/принятое1/недостачу2. Для маркированного дополнительно вычисляет точное исходное подмножество original_source_units minus source_units; количество сверяется точным Decimal с receipt.Expected-Actual. Отображает printed unitID, количество/UOM, текущие UID/cell/status/version и count кодов без раскрытия QR. Изменившееся текущие состояние выделяется как требующее расследования, а не как доказательство потери. Максимум10000 исходных/полученных единиц. Никаких записей запаса/марок/ответственности/GovACK.

Raw interwarehouse UI выбирает ранее принятую поставку и показывает сверку. Актуальные actor/API и serial защищают от позднего ответа; read не создаёт durable write intent.

Фактические291 и292:3/1/2, ordinary0units; marked2 неполученные ISSUED/по2кода, custody остаётся открытой, protected20-20. Browser/independent не проведены. Реальный акт утраты/позднее получение/разрешение ответственности ещё не реализованы.

SQL: первый cold JSON_TABLE 19.589ms/815buffers на2 executions, следующие две чтения добавили36buffers и~2.55ms в среднем. Bounded missing JSON + physical-key unique lookup; явно выбран nested loop и существующий RRL_RECEIPT_UNIT_PHYSICAL_UK, code count по RRL_WMS_REC_CODE_PAL_IX. Новый индекс/cache не нужен.
"""
for path,line in [
("wiki/index.md","- [Сверка недостающего товара](database/nicora_ni061_shortage_reconciliation_20261011.md):294 declared/accepted/short2, exact marked missing subset/currentstates/codecounts/one scoped snapshot."),
("wiki/log.md","2026-10-11:294 scoped oneRO shortage reconciliation API/rawUI. Actual291ordinary3/1/2 and292marked2ISSUED/4codes/custodyopen/protected20-20. Exact frozen unit subtraction/Decimal count, currentstate conflicts/bound10000; existing physical-key/code-pallet indices/NL. No loss act or phantom receipt."),
("wiki/runbooks/nicora_active_work.md","LatestApp294/native293/serv294: shortage read one scoped snapshot; tmp/case294_291.json and tmp/case294_292.json actualshort2/current2ISSUED4codes/no custody release. App629/0cycles76. Next explicit confirmedloss versus recoveredgoods; quantities never invented."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md","11.10.2026:294 Диспетчерская сверка недостачи показывает3/1/2 и для маркированного товара две исходные неполученные единицы/четыре кода/текущее состояние. Приёмка/ответственность/ACK не изменяются. Разрешение недостачи остаётся.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("294 oneRO shortage reconciliation exact missing marked subset/currentstates/printedIDs/profilecodecounts; actual291-292 short2");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI06.1/294_shortage_reconciliation.md").as_posix()]="""# Qwen294: сверка недостачи
Прочитать wiki/database/nicora_ni061_shortage_reconciliation_20261011.md; источники291/292 уже существуют. Не перерождать fixtures.
GET receipt291/292/shortage:3/1/2; marked две ISSUED единицы по2кода; количество не умножается на число систем. Current actor/right/source-or-target WARE обязательны, foreign403. Не выдавать rawQR. Missing key/state/quantity mismatch выделяет конфликт, не подтверждает потери. Browser auth/API-switch/late response; protected20/20/stock/custody/units unchanged.
"""
# Cold history293 dynamic sampling resolved with statistics: next execution1.12ms/12buffers.
p=Path("wiki/database/nicora_ni061_incident_close_20261011.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nSQL293: cold history228.536ms/298buffers included optimizer dynamic sampling199.195ms; gathered DBMS_STATS only additive journal. Next actual history~1.120ms/12buffers. Decision: keep bounded51/unique incident join and refreshed stats; no index/cache/rewrite.\n"
p=Path("db/migrations/2026-10-11_ni061_marked_partial/rollback.sql");s=p.read_text(encoding="utf-8")
s=s.replace("select count(*)into n from RRL_INTERWARE_RECEIPT r join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=r.ROOT_UID where r.ORIGINAL_ROOT_UID is not null;","select count(*)into n from RRL_INTERWARE_RECEIPT r join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.OPERATION_ID where r.ORIGINAL_ROOT_UID is not null and json_exists(o.RESOLVED_PLAN_JSON,'$.domain.source_units[0]');")
out[p.as_posix()]=s
out["wiki/log.md"]+="\n2026-10-11: marked292 rollback refuses retained receipt frozen source_units proof even after later unit relocation; guard no longer depends on mutable CURRENT_UID. Rollback not executed on retained history.\n"
print(json.dumps(out,ensure_ascii=True))
