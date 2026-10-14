# NI07.2 — несколько мест в зоне ожидания

1082 PREPARED. Миграция 2026-10-13-013-ni072-shared-wait-target. При выполнении уже созданного HU1154 и CASE1155 старое правило HU запрещает другой открытый приход в общую ячейку: ORA20886/HU_MOVE_TARGET_HAS_OPEN_ARRIVAL. Отказ не изменил P20/H20; планы сохранены.

Исполнитель остаётся RRL_STOCK_POSTING_API → RRL_STOCK_HU_CMD. Ослабление требования пустоты разрешено только после describe текущего решения ожидания: права, склад, рейс, конфигурация, полный состав собственного Root, target и отсутствие физических slots проверяются прежним обработчиком. Generic HU сохраняет эксклюзивный target. Конкуренция сериализуется существующим CELL fence/anchor; target_json и ограничения назначения сохраняются. Это зона ожидания, а не адрес одиночного хранения. Завершение повторно проверяет источник/решение под объявленными блокировками.

Отдельно display исключает cohort_manifest из сравнения физического источника CASE; сам manifest продолжает проверяться при проведении. Парные свежие исходники1081, checksum, rollback без изменения данных; live compilation и выполнение двух мест ожидают.

1085: явный параметр только у доверенного HU_TASK compile(planning), либо существующий physical WAIT task. Generic HU_MOVE не получает разрешение общей зоны из произвольного metadata/defer ID. Caller ACL и обычное API неизменны. FreshHU spec/task capture перед применением; actual1080 уже DONE/P20H20, отрицательный generic-call ещё ожидает.

1087: twoTOP case reached A_DONE then B correctly rolled back at execute second empty-target guard. Execution now independently describes actual registered WAIT task under Root locks before shared-target exemption; general HU_MOVE remains exclusive. RRL_STOCK_HU_SLOT target_json and frozenplacementcomparison retained. Resume original Boperation/body; no new stock.

1089 APPLIED_DEV_VALID: actual1080 mixedHU8+CASE12/1154+1155DONE and1086 twoTOP12+8/1157+1159DONE, both P20/H20/unchanged exact replays. Generic metadata bypass refused. Current read/UI/changed-path gate PASS; [отчёт27](../../reports/nicora/2026-10-13/27-mixed-place-wait-report.md). Independent acceptance/slots-capacity/mixedFULLPAL remain open; earlierPREPARED and intermediate refusals above are historical.
