# NI04.1 — существующий CASE в отдельном физическом слоте
10.10.2026.076 APPLIED RABAEV/orcl. Inventory/root transaction RRL_STOCK_POSTING_API.

Расширен прежний RRL_RECEIPT_SLOT_CLAIM: nullable FK HU_CASE_TASK_ID и unique CASE owner. Каноническое имя места CASE:<task_id> соответствует существующему HU read model; строка RRL_PALLETS для CASE не создаётся. CONTENT_VERSION CASE связывает свежие SI измерения с актуальным составом.

HU_UNPACK поддерживает child_case_task_id и физическое извлечение в отдельный свободный STORAGE_SLOT. Новый claim/task/SYNCED принадлежат CASE, товар остаётся на прежних CASE_CARRIER_LOT UID. Резерв получает новый слот при сохранении владельца и P/H. CASE после unpack WAIT_CONTROL, старый допуск отозван. Остальные HU и CASE вместе учитываются в агрегатной вместимости; неизвестные измерения блокируют назначение.

Existing CASE_CARRIER_MOVE, CASE_CARRIER_RETURN и SHIP_PALLET заранее включают CASE claim/slot в closure и освобождают его при фактическом уходе. Shared placement core содержит единственное declare/release правило. Measured claims неизменяемы: direct UPDATE запрещён, DELETE только действующий root IN_FLIGHT в той же транзакции с ROW/SLOT locks. Это metadata guard, не механизм изменения запаса.

Авторский scripts/ni041_case_slot_case.py passed: native CASE12+8→existing top placement task→unpack CASE12→две измеренные claims30kg/P20/H20/no quantity journal/replay/no fake PP→existing CASE move12/H12 со свободным старым слотом. Cleanup moved parent8, detached/returned both carriers, own P/H0 retained history. При первой проверке исправлена ошибка нового guard: реальное root STATE=IN_FLIGHT, не POSTING; own failed fixture1989fdabd8 очищен через root, без удаления журнала.

API /api/warehouse-hus/unpack-case и ARM поддерживают CASE identity/scan/current versions/durable retry. Прямое CASE slotted relocation и перепаковка в уже занятом слоте пока требуют explicit unpack + existing move/work area; штатный CASE move target — system control/staging. Equipment assignment uses existing WH task resource policy, не новый dispatcher. Independent marked/concurrency/browser acceptance остаётся открытым, весь NI04.1 не закрыт.

076 rollback отказывает при попытке старым кодом интерпретировать CASE claims; forward repair сохраняет историю, checkpoints368–372 и previous075 sources retained.
[076](../../db/migrations/2026-10-10_ni041_case_slot/apply.sql) · [[nicora_ni041_stock_leaf_20261010]] · [[nicora_ni041_fullpal_hu_shipping_20261010]].

Slow SQL076:9nsd2jjq1h9v1 existing related ST closure11.694ms/2;dv1jzypwv1f8f other-claim read3.994ms/3;case claim deletion c0utwbptx1fsu3.632ms/1. Decision: bounded closure/cell/UID retained; NI08 actual volume-plan review, no guessed changing-counter index.
