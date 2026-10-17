# Температурный допуск CASE и дерева HU

Статус dev APPLIED:13 SHA совпали, USER_ERRORS/INVALID0. Смешанное дерево ASM+BOX24+EA1 принято программно; interWARE/manifest/handover и аппаратная приёмка остаются открытыми.

MIGRATION_ID `2026-10-16-hu-thermal-admission`; [комплект](../../db/migrations/2026-10-16_hu_thermal_admission/README.md), [fresh source checkpoint](../../reports/retailcase/2026-10-16/mixed-hu/native-before/manifest.json).
Frozen manifest SHA `b5e33a6197bba424a9a3e25e23d220597a758aa90b32f595b1d6b63dbabac890`.

## Модель

Сохраняются `RRL_RECEIPT_SKU_RULE.TEMP_MIN/MAX` и `RRL_RECEIPT_CELL_RULE.TEMP_MIN/MAX`; нового справочника зон/температур нет. Уточнение первоначального discovery: HU_MOVE уже проверял отдельные SKU через `RRL_STOCK_HU_SLOT.target_json` (`HU_TARGET_TEMPERATURE_RULE_FAILED`). Новый слой делает общий допуск явным, запрещает known+unknown и дополняет CASE move, attach и ship. Прежний slot owner сохраняется.

Новый чистый `RRL_HU_THERMAL_READ` вычисляет пересечение требований различных SKU из серверного snapshot. Диапазон ячейки должен целиком лежать в общем диапазоне товаров. Пример тестового норматива:0…8 и2…6 дают2…6; ячейка2…6 допускается,20…25 отвергается. Это не рекомендации по хранению реальных товаров: значения производственного справочника задаются отдельно.

Частичное правило SKU, непересекающиеся диапазоны, известный холодный SKU вместе с неизвестным, отсутствующая/несовместимая ячейка дают явный отказ. Когда все правила отсутствуют, прежние операции сохраняют статус UNSPECIFIED и не обозначаются термически проверенными. Пустая упаковка не добавляет требование товара. Будущий строгий manifest может требовать known policy. `policy_only=true`, `observed_temperature_c=null` всегда; датчик не моделируется нормативом.

## Native граница

CASE_CARRIER_MOVE/HU_ATTACH/HU_MOVE/HU_SHIP вычисляют допуск при compile и повторяют его под прежними CONFIG/cell/stock/CASE fences до эффекта. Изменённый допуск — CLOSURE_CHANGED; DETACH остаётся доступным для разборки/исправления. Количество, ST/CASE versions, ownership тары и stock writer не заменяются. Для writer используется также прежний pure `RRL_INTERWARE_THERMAL.assert_cell`.

Helper читает только существующие таблицы:200 суммарных узлов,2097152 символа на каждый входной CLOB (не UTF-8 bytes). Native producer получает resolved snapshots, клиентская «проверка пройдена» не принимается. HU preview добавляет результат в исходном READ ONLY scope snapshot; архив отгрузки получает HISTORICAL_NOT_EVALUATED, без подмены архивного факта сегодняшним правилом.

## Проверки и восстановление

15 focused tests PASS (прежние13 scope +2 thermal boundary), quality gate PASS:1098файлов/0циклов/debt72,tooling24,обаTS. Native [readback](../../reports/retailcase/2026-10-16/mixed-hu/root-readback.json):13SHA/ledger/compile PASS. [Матрица v2](../../reports/retailcase/2026-10-16/mixed-hu/thermal-matrix-v2.json):15 checks/полный rollback правил/max14.45мс, включая точный native proof без изменений и отказ после изменения допуска. Первая матрица не доказывала неизменный proof из-за Python reserialization; v2 исправляет тестовый стенд. Конкурентная смена policy под CONFIG ещё не принята отдельно.

### Смешанное физическое дерево

[ASM subtree](../../reports/retailcase/2026-10-16/mixed-hu/asm-tree.json), [обычный отбор](../../reports/retailcase/2026-10-16/mixed-hu/ordinary-child.json), [pack](../../reports/retailcase/2026-10-16/mixed-hu/mixed-pack.json): root `MH16.TOP:d076c19e82` → BOX → ASM CASE1140 и прямой обычный CASE1142. Три уникальных STOCK листа:1+24+1 EA, всего26; отдельные native операции создают разные carrier lots. Это одна тестовая SKU, не аппаратный тест смешанных товарных температур. Матрица правил отдельно использует две SKU.

CASE1142 прошёл новые typed CLAIM/START, BOX24/EA1 pick и CLOSE/replay с flat CASE_PICK_EXECUTE на домашнем WARE1 плюс explicit WARE20220394 role (`legacy=0/scoped=1`). Тип32 требует измерения пустой тары даже при обычном отборе: выполнена отдельная TEST EMPTY_TARE, без ASM session/step на этом CASE. Нарушение этого guard не обходилось. Скан коробки имеет выделенный QA BARCODE_KOR; количество передаётся накопительно24→25 в base EA.

Обе CASE связаны с разными исходными ST через прежний bind owner до упаковки; перенос/attach обновляют версии fulfilment прежним owner. Положительные CASE move/attach и целое холодное HU move прошли caller rollback; move/pack commit+точный replay приняты. Чужая ячейка, цикл, stale version и горячая цель отвергнуты. ASM_FINAL остаётся историческим основанием сборки, а не shipping QC. Нормативная тара внешних контейнеров и MANUAL_CONFIRMED measurements — только TEST, не внешнее взвешивание.

Три свежие system-ячейки MH16G/B/S существуют только для этой QA: явный LIMIT_HEIGHT0, LIMIT_WEIGHT1000kg, правила холод2…6/горяч20…25. Прежние ячейки не менялись. SKU AS16A35CEA92C27 получила QA правило0…8 и уникальный QA barcode коробки; fixture сохранена для manifest/interWARE. Истории и stock не удалять, stage scripts не повторять; все новые temporary grants уже отозваны.

[HTTP/SQL](../../reports/retailcase/2026-10-16/mixed-hu/http-sql.json): роль позволяет CLOSE replay, отзыв даёт403 несмотря на flat на другом складе; admin preview отдаёт ADMISSIBLE/observed=null.3HTTP/max333мс/INVALID0. Одна slow-log запись и12 V$SQL cursors сохранены. Решение: сохранить bounded/PK запросы и CONFIG fences; без предположительных индексов/кэша. Владелец inventory/native измеряет join plans на объёме пилота. Shared cumulative means не являются p95 этого кейса. Независимый review и реальное оборудование не выполнены.

Сохранён [Python before image](../../reports/retailcase/2026-10-16/mixed-hu/python-before/warehouse_hu.py), SHA `DD18D856AADC24821EEA926BA22C98FE8C9397AC984A74B0F2D9C145D4C5F20D`. Парный rollback сначала требует вернуть Python consumer, затем восстанавливает3 native bodies и удаляет чистый helper. История/количество не удаляются.

Manifest ожидаемых детей, CASE-aware interWARE и handover поддерева, аппаратная приёмка и SHIPPING_GROSS остаются отдельными незавершёнными переходами [[../concepts/retailcase_nested_hu_consolidation_20261015]].
