# NI04.1 — вскрытие в отдельный слот
10.10.2026.069/070 APPLIED в RABAEV/orcl. [[nicora_ni041_slotted_unpack_design_20261010]] реализован в ограниченном сценарии. [[nicora_ni041_multi_hu_slots_20261010]].

HU_UNPACK переиспользует HU_DETACH executor, existing warehouse task/claim и RESERVE_CORE.move_coverage. Верхний parent/непосредственный CONTAINER child/та же ячейка/разные published STORAGE_SLOT; parent сохраняет товарные листья. Обычный leaf, прямой CASE, пустой parent и nested-parent пока explicit refusal, отдельное расширение.

Две fresh SI measurements после физического вскрытия проверяются отдельно и вместе: старое occupied parent исключается из aggregate, заменяется двумя частями, сохраняются loads остальных occupied/incoming мест. Новый slot должен быть свободным. Требуются идентификаторы parent/child, сканы ячейки и двух slot codes, обе expected versions, причина.

Root объявляет old/new SLOT/CELL_X/complete HU/CASE/ST/stock/unit/reservation и два task/claim/sync IDs. Повторно проверяет actual tree/placements под closure, деактивирует link существующим executor, increments HU versions и отзывает CASE QC. Создаёт две реальные DONE MANUAL/PUTAWAY задачи1HU/FACT1 и два fresh guarded claims; это подтверждённое сканируемое действие, не новая очередь и не утверждение автоматического измерения прибором.

P/H/units/owner/UID/cell сохраняются. Только существующее move_coverage всей HARD записи меняет child CELL_SLOT_ID и reservation version, сохраняя identity/количество/владельца. Root journal quantity events0; immutable operation/result и outbox описывают physical action. Оба task sync SYNCED записываются атомарно. Existing sync retry для HU_TASK_COMPLETE/HU_UNPACK проверяет immutable root result/actual task identity и не требует фиктивного movement quantity1HU=товарный BASE.

070 расширяет existing RRL_WH_TASK_STOCK_MOVE_U1 с TASK_ID до TASK_ID,UID_PALLET: одна строка каждого фактического товарного листа составного HU. Прежний single-leaf executor без изменений; долг FULLPAL preview выбирает только WAVE/PICKING_MOVE. Rollback не удаляет историю и отказывается вернуть single-task unique key, если уже существуют multi-leaf facts.

Own scripts/ni041_slotted_unpack_case.py passed: actual HU placement двух листьев5+5/H2 (две stock facts), unpack parent20kg/child30kg и объёмы.75+.75, два claims/version/current-slot, P10/H2 unchanged/same HARD identity/new child slot/no quantity journal/exact replay. Bad scan/110kg total отказаны; retry sync original HU task и обоих new done tasks возвращает SYNCED. Own P/H и claims очищены root после whole move и явного unpack; документы/журнал оставлены.

API POST /api/warehouse-hus/unpack, server actor/right warehouse_task_execute, typed measurements/versions/scans. ARM принимает отдельные свежие измерения parent/child и сохраняет pending body для exact retry. JS syntax и OpenAPI endpoint проверены; independent browser/concurrency/equipment acceptance ещё не выполнена.

Slow SQL child reservations1jbf2cv6sqmad ~8.12ms/1; corrected JSON path query7vq0t8w5vkbt4 ~7.79ms/1, bounded tree UID matrix + sorted reservation IDs. Решение — bounded/key access, наблюдать batching на больших HU (NI08 inventory owner); без нового индекса. Миллионы/day этим case не доказаны.

Дальше: same-cell slot transfer, прямой CASE/ordinary leaf/pустой parent, equipment sessions, upper FULLPAL shipping/route gate и независимая acceptance. NI04.1 не закрыт целиком.
