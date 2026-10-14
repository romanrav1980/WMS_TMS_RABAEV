# NI04.1 — несколько верхних HU в ячейке
10.10.2026.068 APPLIED в RABAEV/orcl. [[nicora_ni041_hu_slots_20261010]].

Существующие HU warehouse tasks могут занять разные физические STORAGE_SLOT одной ячейки. Claim занятого/зарезервированного слота и открытое поступление в тот же слот исключают повторное назначение. Неслотовое движение сохраняет прежнее требование пустой ячейки. Same-cell смена слота и slotted unpack ещё не реализованы.

Общая масса/габаритный объём ячейки включают действующие occupied HU claims и открытые incoming warehouse tasks с frozen SI measurements. Limits topology/cell применяются к сумме, limits каждого slot к своему HU. Ранее неизвестные единицы массы/размеров, простые receipt claims и несопоставленные остатки не переводятся догадкой: explicit refusal, отдельный NI04.2 ticket.

На существующем RRL_RECEIPT_SLOT_CLAIM добавлены HU_GROSS_WEIGHT_KG/HU_BOUNDING_VOLUME_M3/HU_COMPOSITION_VERSION. HU_TASK_COMPLETE после actual move фиксирует подтверждённые SI measurements и новую версию parent. Guard разрешает создание только этой root-команде, запрещает правку measurements и требует совпадение версии; legacy ordinary claims сNULL сохранены. Старый claim после ухода удаляется существующей root-проводкой, документация задачи и operation остаются.

Проверка существующих top roots сверяет claim/version и bounded реальное HU дерево. Stock в целевой ячейке должен быть покрыт измеренным top HU; лишний stock запрещён. До200 existing/arriving roots и20000 nodes на суммарный просмотр, каждое HU ранее bounded200/depth16. CELL_X сохраняется для корректной проверки aggregate; параллелизм разных ячеек остаётся. В план не записывается изменчивый общий load: completion повторно проверяет actual+planned capacity и сравнивает только собственный frozen placement.

Own scripts/ni041_multi_hu_slot_case.py passed: два existing MANUAL/PUTAWAY task50kg/1.5m3 в distinct slots; первый ещё incoming, второй51kg отказан при общей capacity100kg. Same planned slot denied. Оба complete→одна ячейка P10/H2, два claims100kg/3m3, owner preserved, exact replay. Оба места затем moved в свои рабочие ячейки, unpack/release/count0 выполнены только для собственных fixtures.

API target-slots больше не помечает всю measured HU cell занятой из-за другого слота; actual capacity/coverage решает root command. ARM пояснение обновлено. Browser, real measured equipment и concurrent acceptance не заявлены.

Slow SQL: existing incoming8ns44jv0uq47f ~0.62ms/16, claim sumf91gv5hvcdb8r ~3.91ms/2. Решение — bounded roots/trees и keyed claim lookup; для больших cells повторный per-root snapshot может потребовать batching (NI08 inventory owner), индекс без измеренного bottleneck не добавлен.

Remaining: slotted unpack, same-cell slot transfer, ordinary receipt/manual measurement adoption, FULLPAL leaves/upper shipping route policy and independent concurrency/browser/marked cases.
