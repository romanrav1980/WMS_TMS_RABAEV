# NI04.1 — товарная паллета и пустая внешняя тара
10.10.2026.074 APPLIED RABAEV/orcl. inventory owns place/stock, authoritative Oracle, root transaction RRL_STOCK_POSTING_API. Полный спринт остаётся открытым.

HU_UNPACK позволяет извлечь STOCK leaf в другой свободный STORAGE_SLOT этой же ячейки, сохранив пустую внешнюю CONTAINER тару в прежнем слоте. Обоим местам необходимы новые подтверждённые положительные SI измерения; система не делит массу по количеству. Использованы прежние DONE MANUAL/PUTAWAY задания и SYNCED записи, отдельные claims; HARD сохраняет владельца и получает новый слот без изменения P/H и количественного журнала.

Измерение товарной паллеты связано с HU_CONTENT_VERSION, STOCK_COMPOSITION_VERSION и digest текущих физических единиц; PHYSICAL_VERSION ячейки сохранён как evidence. Резерв не меняет физический состав. Исправление и возврат количества не восстанавливает старую массу: существующий claim требует нового измерения. HU_RELOCATE_SLOT обновляет измеренное место явной командой; отдельный HU_MOVE позволяет вывезти пустую внешнюю тару без вымышленной проводки товара. Существующий целый INTERNAL_MOVE освобождает claim источника.

Совместное размещение учитывает measured standalone STOCK и CONTAINER roots и planned arrivals, сохраняет лимиты200 мест/20000 nodes+units и fail-closed для неизвестной массы/состава. CASE identity по-прежнему отдельная, direct CASE placement в074 не включён; фиктивные товарные PP для CASE не создаются.

API contracts сохранены; ARM принимает STOCK child при вскрытии и STOCK root для смены слота. Авторский scripts/ni041_stock_leaf_case.py проверяет P5/H2/owner/слот/replay/epoch и очистку собственной поставки. Результат runtime log — авторское evidence; независимые concurrent/marked/browser cases остаются открытыми.

Rollback автоматического понижения версии отвергается: старые правила не понимают stock claims и пустую тару. Forward repair сохраняет task/claim/link/operation history. Предыдущие исходники находятся в071, новые —074.

Источники: [074](../../db/migrations/2026-10-10_ni041_stock_leaf/apply.sql), [[retailcase_ni042_composition_epoch_20261010]], [[retailcase_ni041_slot_relocation_20261010]].

Авторский case passed полностью: P5/H2 extraction, leaf slot change/replay, H-only valid,6→5 stale claim denied, fresh measurement, empty carrier move and existing stock INTERNAL_MOVE cleanup P/H0. Slow SQL9kd0vwcd5z3nh measured claim read5.532ms/1;1jr5xmkk3mfr0 unknown-claim bound4.019ms/3; DDL261–309ms excluded. Decision: bounded cell/UID reads retained, no new index justified; NI08 warehouse-volume plan check. Target-slots read projection recognises valid standalone stock claims; root remains capacity authority.
