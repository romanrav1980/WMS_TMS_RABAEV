# NI04.1: существующий CASE внутри складского HU

054 APPLIED в RABAEV/orcl. Read/cmd/transfer/link guard VALID; checkpoints316–318. [[nicora_ni041_hu_slots_20261010]].

Ветка CHILD_CASE_TASK_ID ссылается на существующий RRL_CASE_PICK_TASK, листья читаются из прежнего RRL_CASE_CARRIER_LOT. Новые товарные паллеты и строки остатков при упаковке не создаются. В упаковку допускается закрытый физический CASE (WAIT_CONTROL/CONTROLLED/READY_TO_SHIP), в той же ячейке/складе; незаконченный отбор и контроль в процессе не допускаются.

У CASE один активный parent по прежнему unique index. Root упаковывает/вскрывает с двумя версиями состава и физическими сканами, блокирует CASE/task/wave/link/leaf stock/reserve/unit вместе с ancestors; CT.CONTENT_VERSION и события HU_PACKED/HU_UNPACKED обновляются в одной транзакции. Операторский read сканирует прежний SSCC CASE, а parent остаётся существующим container UID. Типизированные attach-case/detach-case и общий ARM используют эту identity.

Whole HU move переносит каждый прежний лист, резервы и марки через RRL_STOCK_TRANSFER_CORE; для CPT используется уже существующий CASE_EXIT. CASE.CURRENT_CELL/CONTENT_VERSION и HU_CARRIER_MOVED записываются вместе с движением. Запрет количественного изменения вложения действует также на CASE: отдельный CASE_CARRIER_MOVE/return/shipping не может провести P до явного unpack. Regulatory CRPT aggregation не изменяется автоматически.

Исторический gross исходной паллеты нельзя выдавать за массу CASE-листа; она показывается неизвестной. Неизвестная масса тары CASE тоже не заменяется подтверждённым нулём. Для ограниченного слота требуется manual-confirmed whole gross из053; подключение весов и регуляторная переагрегация остаются отдельными slices.

Адресный dev case scripts/ni041_hu_case_carriers_case.py: существующая wave12+8/replenishment20/release/CASE physical close → два CASE под одним roll cage → одна whole move20/H20 → owners/locations сохранены → replay → explicit unpack → прежний return/cleanup собственного P/H. Отдельный CASE move в существующую system ячейку внутри parent получил именно NESTED_HU_REQUIRES_TOP_MOVE_OR_EXPLICIT_UNPACK и откатился. Это не доказательство готовой погрузки/выезда или regulatory acknowledgement.

SQL: HU read3uwrpkb9x39z1 4.64мс/10, APIread7.43мс, carrier lookup1rhq60xupx1c6 0.71мс/4. Решение — общая граница200 узлов/depth16 и существующие PK/member lookups, без дополнительного индекса; диагностические V$SQL запросы исключены.

Открыто: несколько мест/ячейка, погрузка/отгрузка верхнего HU с одним атомарным фактом и существующим контролем, полный marked/browser/concurrent independent scope. Статус NI04.1 in_progress.
