from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for dirname in ["2026-10-12_ni061_nested_placement","2026-10-12_ni061_nested_custody"]:
 d=Path("db/migrations")/dirname
 out[(d/"000_before_manifest.json").as_posix()]=p.read_text(encoding="utf-8")
 for sql in sorted(d.glob("*.sql")):
  if sql.name.startswith(("000","009")) or sql.name in ("apply.sql","rollback.sql","verify.sql") or "ledger" in sql.name:continue
  entry="../"+dirname+"/"+sql.name
  if entry not in m["additional_scripts"]:m["additional_scripts"].append(entry)
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
page="wiki/database/retailcase_ni061_nested_completion_20261012.md"
out[page]="""# Целое вложенное место: размещение, ответственность и доставка

317–318 APPLIED в выделенной RABAEV/orcl. 319 фактически завершил цепочку source316: SAP birth 3 EA / 6 исходных кодов → первое HU-плечо → межскладская приёмка 314 той же TOP/BOX/STOCK структуры → размещение 317 → ответственность 318 → второе плечо → магазин принял 3 EA. Итог P0/H0, исходное исполнение заказа SHIPPED3 ровно один раз; независимый запас P20/H20 сохранён.

Размещение использует прежнее задание WAREHOUSE_HU, количество задания 1 HU; товарный факт прежнего журнала размещения 3 EA. RRL_STOCK_HU_TASK вызывает существующий RRL_STOCK_INTERWARE_PUT для ресурсов, проверки и подтверждения. Прежний HU_CMD перемещает всю структуру. PUTAWAY разрешён только для точного native interwarehouse_placement proof; обычное движение из недоступной карантинной ячейки не разрешается. Цель выбирается существующей политикой ячеек. Поздний rollback восстановил исходную ячейку, запас, ссылки и отсутствие факта размещения. Повтор вернул тот же результат.

Ответственность снимается с фактического верхнего места SOURCE_PLACE_UID; товарный ROOT_UID сохраняется для остатков/маркировки. Старый guard load-fact проверяет исходный APPLIED receipt и родительский plan. История отправления и исходных закрытых ссылок сохранена.

Второе плечо использует прежние подготовку СТ, назначение, QC, HU_SHIP, departure и STORE receipt. Верхнее место IH316 и коробка IB316 не создавались заново и не перепаковывались. Сохранено шесть исходных кодов; повторное исполнение заказа и новая маркировочная birth запрещены.

320: операторские queue/incoming показывают SOURCE_PLACE_UID как идентификатор физической паллеты, ROOT_UID отдельно как stock_pallet_identifier. Артикул/количество/единица извлекаются из единственного STOCK узла исходного архива, а не из верхнего CONTAINER. Отгруженное количество incoming берётся из факта dispatch.

Границы: одно СТ и один STOCK лист в CONTAINER-only дереве до 200 узлов. Частичная nested-приёмка, много СТ/товарных листьев, дальнейший третий склад и HU-replan не заявлены реализованными. Существующий multi-hop guard сохранён. Реальные государственные ответы, оборудование и независимая Qwen-приёмка не получены.

Источники: миграции 314/317/318; scripts/case317_hu_placement.py, case318_custody.py, deliver319_tree.py; tmp/context314_received.json, context317.json, context318.json, context319.json. Фабрики и первоначальные P3 проверки повторно не запускать: груз уже доставлен. Native rollback после сохранённой физической истории требует forward recovery.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Полная доставка вложенного места](database/retailcase_ni061_nested_completion_20261012.md):317–320 existing wholeHU task1/3EA, top custody, same-tree secondleg/customer3, physical-versus-stock read models.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 317–320: actual same-tree SAP/source316/firstleg/314receipt/317wholeHUplacement/318topcustody/319secondleg/STORE3 complete; FF3 once, old6codes, P0/H0, protected20/20. Runtime overrides mirrored; queue/incoming distinguish physical top and commodity leaf. One-ST/one-leaf only; no false external or independent acceptance.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");text=p.read_text(encoding="utf-8");text=text.replace("Current native313/app311/serv311.","Current native318/app320; server restart320 pending.")
out[p.as_posix()]=text+"\nCurrent320: source316 now fully delivered through actual314/317/318/319, tmp/context319 customer3/P0/6oldcodes. Never rerun factories or initialP3 assertions. Source315 still departed towardcustomer; complete existing STORE next. Runtime manifest now includes317/318 override bodies. WholeHU replan/multiST/multiSKU/partial nested remain explicit bounded gaps.\n"
p=Path("wiki/database/retailcase_ni061_nested_receiving_20261012.md");t=p.read_text(encoding="utf-8");t=t.replace("Whole-HU placement/task/custody/onward continuation ещё не установлены этим314: текущее дерево в receivingquarantine, товар не принят магазином.","Продолжение реализовано 317–319: это дерево размещено целиком, ответственность передана, второе плечо доставило магазину 3 EA; текущий запас P0. См. [[retailcase_ni061_nested_completion_20261012]].")
out[p.as_posix()]=t
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/320_nested_completion.md").as_posix()]="# Qwen 317–320\nПроверь существующее wholeHU задание 1HU и товарный факт3EA; поздний rollback всех остатков/ссылок/ячеек/журналов. Quarantine ORDINARY отказ, только точный PUTAWAY native proof. Ответственность верхнего места, stockleaf отдельно. Source316 уже доставлен: factories и первоначальныеP3assertions запрещены; context319 exact repeat безопасен. Очереди показывают физический TOP, артикул и qty3 из STOCK, dispatchqty3. MultiST/partial/multihop/HUreplan не поддержаны. Независимое выполнение заданий ещё не проведено.\n"
print(json.dumps(out))
