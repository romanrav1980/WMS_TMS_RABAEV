import json
from pathlib import Path
out={}
page="wiki/database/retailcase_ni043_aggregation_lifecycle_20261012.md"
out[page]='''# NI04.3: локальная отмена исходной агрегации
Дата: 12.10.2026. Native migration: [450](../../db/migrations/2026-10-12_ni043_aggregation_lifecycle/apply.sql), актуальные правки454/456/457/463. Owner: inventory, единственный writer остатков прежний RRL_STOCK_POSTING_API. Локальная отмена — metadata-транзакция с CONFIG X; журнал пишет существующий RRL_REGULATORY_API. Государственная квитанция не создаётся.

Команда RRL_TRACE_AGG_LIFECYCLE.invalidate принимает идентификатор операции, склад, исходную паллету, систему/профиль, SHA256 кода, причину OPENED/REPACKED/DAMAGED/COMPOSITION_CHANGED и документ. Право trace_manifest_import, актуальная привязка пользователя к складу. Требуется точный применённый оригинал: SAP receipt/order-line или использованный sender manifest. Отменять можно код исходного состава, даже если при рождении сканировали только его родителя. Все физические единицы именно этой агрегации должны находиться на указанном складе, быть AVAILABLE без hard reservation. Наличие другой единицы того же origin на складе не даёт права отменять чужую коробку.

Неизменяемые RRL_TRACE_AGG_INVALIDATION и RRL_TRACE_AGG_BLOCK сохраняют причину, автора, журнал и affected codes. Непосредственный код и все точные родительские узлы исходного sender graph блокируются совместно. Для плоского SAP состава BOX блокирует PALLET того же профиля, если PALLET содержит все единицы BOX. Соседние коробки не блокируются. Родительская отмена сама по себе не отменяет закрытые дочерние коробки. Лимиты: до1000 affected aggregates, до10000 физических единиц. Повтор с тем же actor/request возвращает исходный результат; другое содержимое отклоняется. Уникальность и CONFIG X сериализуют конкуренцию. Восстановления старого кода нет: новая упаковка требует нового подтверждённого состава и отдельного regulatory lifecycle.

RRL_IW_AGG_SCAN вызывает единый assert_scan и сохраняет прежние проверки qty/profile/version/issued fingerprints. Дополнительно текущий UID каждой исходной единицы должен совпадать с origin: оригинальный код не разрешается автоматически для товара, переложенного в новый товарный паллет/CASE/возвратный UID. Перемещение целой исходной паллеты допускается. Это не доказывает неприкосновенность пломбы; операционная фиксация вскрытия обязательна.

HTTP:
- POST /api/inventory/trace-manifests/aggregations/invalidate — typed strict request, durable original operation ID.
- GET /api/inventory/trace-manifests/warehouses/{ware}/pallets/{origin}/aggregations — warehouse-scoped READ ONLY, до1000 оригинальных/scanned codes. REGISTERED_EVIDENCE не означает разрешённый скан или государственное подтверждение.
- В существующей странице pallet-composition добавлена панель жизненного цикла. Отправка требует права, причины и документа; неопределённый результат сохраняет точный payload в localStorage на actor/API и даёт повторить его. Отдельная отмена не меняет остаток и коды единиц.

Авторские доказательства:
-452: native полная отмена/повтор/content conflict/late rollback; P3H0, event1,6codes неизменны.
-459: unscanned CRPT.BOX1 в sender124 блокирует только BOX1 и её PALLET, BOX2 остаётся доступна относительно этого правила; rollback возвращает0facts/P3.
-462: реальные конкурентные HTTP200/200 одного operation ID, одна отмена/одинjournal/2blocks; повтор/conflict/custody отказ; P3H0/event1/6codes/protected20H20 сохранены. Сохранён tmp/context462.json. BOX1 и PALLET sender124 теперь намеренно отменены; не повторять исходный сценарий459.
-464/465: свежий SAP ARTMAS/supply, birth3/6codes, исходные сканы2, native приёмка3/6/late rollback; первый HTTP после recompilation вернул непроверенный503, точный повтор того же ID успешно проведён один раз. tmp/context464.json — принятая паллета в карантинной ячейке. Не повторять source464/case464 initial.
- Live Oracle: USER_ERRORS/INVALID empty. Architecture647/0cycles/76debt PASS. JS node--check PASS. Браузерное и независимое Qwen ревью не выполнено.

Ограничения: нет реального ACK государственных систем/сертификатов/сканера; автоматическая юридическая переагрегация и новый государственный код не заявлены. Partial/group aggregate-only receiving остаётся отдельным инкрементом. Отмена локально блокирует межскладской aggregate scan; прочие сканирующие потоки должны подключать этот же контракт, а не отдельную копию правила.
'''
for filename,entry in [("wiki/index.md","- [Локальная отмена агрегации](database/retailcase_ni043_aggregation_lifecycle_20261012.md):450–465 точный original BOX+ancestor invalidation/native scan guard/metadata journal/no P effect/concurrent HTTP/replay/SAP fresh3.\n"),
("wiki/log.md","\n-12.10.2026 450–465: NI04.3 local immutable aggregation invalidation, exact applied SAP/sender origin+all-free-local custody, sender ancestor closure/SAP BOX-PALLET containment. Original stock owner retained; no quantity/regulatoryACK. Native rollback452/459, actual concurrent462 onefact/twoblocks/onejournal/P3H0/6codes; fresh SAP464/465 old aggregation positive after exact uncertain503 retry. API461/current UI added; original sender124 BOX1/PALLET intentionallyinvalid now.\n"),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_3.md","\n450–465: implemented local immutable original aggregation invalidation+parent closure, existing regulatory journal, exact original-unit custody, native current-origin scan restriction; concurrent HTTP replay/rollback/freshSAP3/6 positive. Government repacking/new-code ACK and remaining scan flows/independent review stay open. Evidence: [[database/retailcase_ni043_aggregation_lifecycle_20261012]].\n")]:
 p=Path(filename);old=p.read_text(encoding="utf-8");out[filename]=entry+old if filename=="wiki/index.md"else old+entry
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
m["planRevision"]=15;m["date"]="2026-10-12";m["currentSprint"]="NI06.2"
for x in m["increments"]:
 if x["id"]=="NI04.3":
  x["status"]="in_progress_local_aggregation_lifecycle"
  x.setdefault("implementedSlices",[]).append("450–465 immutable local aggregate invalidation/ancestor closure/current-origin native scan guard/exact custody/concurrent replay/freshSAP3-6")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
q=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[str(q/"NI04.3"/"467_aggregation_lifecycle.md")]='''# Qwen: NI04.3 local aggregation lifecycle
Read wiki/database/retailcase_ni043_aggregation_lifecycle_20261012.md and current sources. Independent result only after your own cases. Existing context462 is committed: exact replay only, never initial459/source464. Check current actor/WARE rights, exact all members custody vs unrelated local unit, APPLIED original source, unscanned BOX, exact parent closure, unchanged sibling, parent cancellation without cancelling closed children, SAP containment, duplicate/hash conflict, concurrent same/different IDs and transaction rollback including journal/block rows. P/H/physical keys/qty/code identities must remain unchanged. Current UID changed after repack must refuse original aggregate scan. Validate raw UI uncertain-response retry/storage/auth boundary; no false legal ACK/REGISTERED_EVIDENCE admission. Review slow SQL and high-leaf bounds. Report gaps and reproduction without editing protected data.
'''
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name in ["../2026-10-12_ni043_aggregation_lifecycle/001_lifecycle.sql","../2026-10-12_ni043_aggregation_lifecycle/002_scan_guard.sql","../2026-10-12_ni043_aggregation_lifecycle/003_ledger.sql"]:
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/runbooks/retailcase_active_work.md");s=p.read_text(encoding="utf-8")
out[str(p)]="12Oct467: latest NI04.3 local aggregate lifecycle450-465/liveVALID/API461/planrevision15. sender124 BOX1/PALLET intentionally cancelled ctx462; freshSAP464 received3/6 after exact465 retry. Do not rerun source factories or459 initial. Next NI06.2 nonaccepted cargo return.\n\n"+s
print(json.dumps(out))
