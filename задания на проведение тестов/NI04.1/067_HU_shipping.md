# Qwen067: верхняя отгрузка CASE-HU
Отдельная business warehouse/собственные documents, та же RABAEV; никаких общих reset/stock SQL.
1. scripts/ni041_hu_shipping_case.py: actualCASE12+8→existingST/HU/BOTH→HU_SHIP, P0/H0, legacy ST rows retained, departure/history/replay.
2. Проверь отсутствие отдельной nested shipping, bad scan/no approval/stale tree/foreign owner; весь запас/резерв должен остаться.
3. Независимый atomic-failure case: отдельные fixtures, отказ второй внутренней ST после первой; ни первой записи движения/списания/CASE SHIPPED, ни partial outbox/claim cleanup не должно сохраниться. Не добавляй production fault switch.
4. Два соединения QC/HU packing/return/shipping; exact replay same payload and operation, changed payload same ID denied. Упорядоченные logical closure и ST-before-CASE; фиксируй реальные deadlocks/timeouts отдельно.
5. Маркированные два CASE/allprofiles: реестр physical units/issued status, immutable operation, legal readiness gate. Warehouse HU не означает государственную aggregation.
6. API/ARM historical composition explicit; после departure ячейка/slot свободны, товары исторической таблицы не выдаются как живой остаток.
7. Ordinary/FULLPAL leaves пока explicit CASE_ONLY_SLICE refusal; route/dock consistency отдельный остаточный ticket. Не ставь весь NI04.1 DONE.
8. Longest SQL: bounded/key lookup/cache/index/owned backlog evidence.
