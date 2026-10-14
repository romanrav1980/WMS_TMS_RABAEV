from pathlib import Path
import json
out={};page="wiki/database/nicora_ni061_flexible_unit_mode_20261012.md"
out[page]="""# Межскладская приёмка: разрешённое сканирование единиц
Migration 2026-10-12-309-flexible-unit-mode APPLIED в dev RABAEV/orcl. Сохранены live-before package body и runtime manifest; rollback восстанавливает прежнюю проверку режима, запас не меняет.

RRL_INTERWARE_MARK_SCAN уже проверяет матрицу физических единиц × текущих профилей, точный состав и выбранную часть груза. Прежняя проверка ошибочно запрещала UNIT_OR_AGGREGATION. Теперь сканирование единиц допускается для UNIT и UNIT_OR_AGGREGATION. BOX/PALLET требуют агрегацию и не допускают обхода через QR единиц.

case309_unit_mode.py: существующая недостающая единица source307, без повторного рождения товара. Четыре режима проверены в отдельных транзакциях; изменения карточки откатились, исходный UNIT восстановлен. Пропуск профиля/повтор QR отказаны. Package VALID, защищённый P20/H20 сохранён. Это проверка native валидатора; фактическая приёмка по агрегационным кодам остаётся отдельной задачей.

SQL309 8 executions /4.615ms total /18buffergets. Решение: сохранить текущую индексную проверку профилей и ограниченную матрицу; дополнительный индекс/кэш не обоснован.

Источники: [migration](../../db/migrations/2026-10-12_ni061_flexible_unit_mode/apply.sql), [native case](../../scripts/case309_unit_mode.py), [[nicora_ni061_partial_recovery_20261011]], [[nicora_ni043_sender_manifest_20261010]].
"""
p=Path("wiki/index.md");s=p.read_text(encoding="utf-8");s="- [Режим сканирования межскладской приёмки](database/nicora_ni061_flexible_unit_mode_20261012.md):309 UNIT_OR_AGGREGATION принимает точные QR единиц; BOX/PALLET не обходятся.\n"+s;s=s.replace("onramp11Oct/current native302/app303","onramp12Oct/current native309/app307");out[p.as_posix()]=s
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 309 исправлен запрет UNIT_OR_AGGREGATION в прежнем native interwarehouse mark validator; live applied/bodyVALID/exact missing and duplicate QR denial/BOX-PALLET denied/profiles restored/P20-H20. SQL4.615ms total8/18buf: retain bounded indexed matrix.\n"
p=Path("wiki/runbooks/nicora_active_work.md");s=p.read_text(encoding="utf-8");a=s.index("Native manifest302/app303:");b=s.index("## Последняя функциональность",a)
s=s[:a]+"""Current native309/app307/serv308. Recovery301–303 and partial305–306 actual accepted3/sourceFF3once. Cancellation307 and receive-cancel308 actual one winner. Flexible UNIT_OR_AGGREGATION unit capture309 applied; BOX/PALLET aggregate capture remains pending. Arch633/zero cycles/76debt last307. Source contexts preserved; never rerun source factories or initial P assertions.

Current source307: original accepted1 plus found1 in receiving quarantine, one missing unit still ISSUED. No false customer acceptance or full recovery. See context308/307; original physical identities retained. Protected P20/H20 unchanged.

Next: current aggregation validity and exact membership for interwarehouse scans; existing sender and SAP aggregate registries reused. Nested HU_SHIP archives/deactivates links; predeparture UNLOAD cannot restore target stock after DEPART. Real providers/hardware/independent acceptance remain open. No legal ACK invented.

"""+s[b:];s+="\nLatest309 native-only mode fix/bodyVALID; case309 metadata updates allrolledback. No API restart needed. Current manifest309 requires FILES generation, not fullbundle application.\n";out[p.as_posix()]=s
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n309: исправлена совместимость UNIT_OR_AGGREGATION со сканированием единиц; точная native матрица/отказы подтверждены, BOX/PALLET требуют отдельную агрегационную реализацию.\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));inc=next(x for x in j["increments"]if x["id"]=="NI06.1");inc.setdefault("implementedSlices",[]).append("309 native UNIT_OR_AGGREGATION exact unique-unit capture compatibility; BOX/PALLET not bypassed");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/309_flexible_unit_mode.md").as_posix()]="# Qwen309\nПроверь native точную матрицу UNIT/UNIT_OR_AGGREGATION; BOX/PALLET должны отказать QR единиц. Missing/duplicate/foreign QR отказ без P/H/UNIT/outbox эффекта. case309 временно меняет собственную карточку и откатывает её. Не запускай source307/initial receipt заново. Отдельная агрегационная приёмка пока не заявлена выполненной.\n"
print(json.dumps(out))
