# NI04.1 — смена слота в одной ячейке
10.10.2026.071 APPLIED в RABAEV/orcl. [[retailcase_ni041_slotted_unpack_20261010]].

HU_RELOCATE_SLOT переносит целое верхнее CONTAINER HU с товаром между разными STORAGE_SLOT одной ячейки. Quantity/UID/cell/owner/unit membership и warehouse links сохраняются; действующий QC semantic signature остаётся неизменным. Меняются parent technical version, placement claim и CELL_SLOT_ID существующих HARD через move_coverage, без release/reallocation/P/H/journal quantity.

Fresh manual SI measurements/current version, сканы контейнера/ячейки/старого и нового slots, причина и current published topology обязательны. Новый слот свободный. Общая нагрузка проверяется заменой прежнего parent новым placement, с учётом прочих occupied/incoming. BLOCK/temp/dimensions/aggregate limits и repeated version mismatch не обходятся.

Один Root owner объявляет весь tree/stock/unit/reserve/CASE/ST closure, CELL_X/old-new SLOT/old-new claim/task/sync. Повторно проверяет composition/placement под блокировками. Общий RRL_STOCK_HU_PLACEMENT_CORE записывает фактически завершённую существующую MANUAL/PUTAWAY задачу1HU, immutable fresh claim и SYNCED. HU_UNPACK использует тот же core; copied placement writer удалён.

Targeted scripts/ni041_slot_relocation_case.py passed: оригинальное placement two leaves5+5/H2, slotted unpack20+30kg/.75+.75, BOX slotB→C той же ячейки, old slotB free, P10/H2 и та же HARD identity/new slotC, quantity journal0, exact replay и existing sync retry. Bad scan и occupied parent target denied. Own fixtures/root cleanup выполнены. Independent CASE/marked/QC-retention/concurrency/browser/session/equipment acceptance не заявлена.

API POST /api/warehouse-hus/relocate-slot, server actor/warehouse_task_execute, typed version/measurements/scans/reason; ARM reuses saved immutable request/retry. OpenAPI и JS syntax passed.

Отдельно исправлен historical preview отгруженного промежуточного контейнера: departure_subtree выбирает собственных потомков из immutable shipment snapshot, сохраняет historical ancestors и не подменяет дочернее место всем внешним составом. Старый snapshot без per-leaf unit counts возвращает unknown child count; он не угадывается. Existing top departure preview passed, nested actual departure acceptance pending.

Slow SQL occupied claim8xkfxk00msyhg ~0.44ms/6, generic occupied claims a2wsrmu2h6jxs ~0.07ms/68; decision bounded closure/key lookup/shared place writer, без нового индекса.

Структурный gate после accumulated project changes пока FAIL: typed boundaries/oversized legacy services/static dependency cycle требуют отдельного NI00 debt work. Пороги и baseline не повышены. Existing RUSERS auth теперь экспортируется через platform public infrastructure adapter, все API module callers используют тот же authority, включая stock permission constant; API restored/OpenAPI available. Это не заявление full architecture acceptance.

Открыто: direct CASE/stock leaf/empty parent unpack, FULLPAL/ordinary upper shipping and route gate, independent physical/marked/concurrent/browser acceptance и equipment sessions; полного NI04.1 DONE нет.
