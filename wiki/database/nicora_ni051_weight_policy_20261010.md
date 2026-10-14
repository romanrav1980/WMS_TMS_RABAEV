# NI05.1: точный SI вес и допуск

061 APPLIED в RABAEV/orcl: RRL_STOCK_QC_WEIGHT, QC_GATE и PALLET_QC_CMD VALID, checkpoints330–331. [Versioned migration](../../db/migrations/2026-10-10_ni051_weight_policy/apply.sql). Дополняет [[nicora_ni051_quality_binding_20261010]], полный NI05.1 остаётся в работе.

В существующий RRL_RECEIPT_SKU_RULE добавлены QC_BASE_WEIGHT_KG, QC_BOX_WEIGHT_KG, QC_WEIGHT_BASE_UOM, QC_WEIGHT_VERSION. Масса на одну BASE включает первичную/нормированную упаковку товара, но исключает отдельно измеренную тару паллеты. Масса стандартной коробки нужна для бизнес-допуска. Значения задаются явно в кг, базовая единица проверяется по точному UOM справочнику. Не предполагаются единицы legacy WEIGHT_OF_KOR/CARTON_WEIGHT и не переносится константа3.5.

QC ожидает SUM(actual confirmed allocation BASE quantity * configured kg/BASE). Допуск MIN(configured box kg)/2, обе границы включительно. Ошибка/нет полной policy/не совпал BASE_UOM запрещают весовой проход, никаких нулевых fallback или округлений integer. WEIGHT/WEIGHT2 сохраняют legacy различие настройки автоотгрузки, рассчитывают одну и ту же явную массу; failed check отзывает подписи. Изменение mass version входит в состав и отзывает старый scan/weight даже при возврате прежних значений.

SKU policy GET/PUT /api/sku-quality-weight/{warehouse}/{article}; optimistic expected_version, read finished_goods_view, write warehouse_settings_edit. Конфигурация через existing exclusive CONFIG warehouse transaction. Отдельный guard разрешает mass writes только configuration transaction, полный набор полей и increment версии. Primary physical stock writer по-прежнему root.

Панель настройки в product-shipment-settings.html, контроль в warehouse-tasks.html. Нулевая измеренная тара разрешена. API веса не использует ORDER_WEIGHT cache, RRL_PALLET_WEIGHT/2 и RRL_TT_POGRESHNOST. Старые legacy display functions сохраняются пока как отдельный native caller follow-up: их экранные прогнозы ещё требуют переключения на новый read contract; они не определяют root QC результат.

Targeted own case passed: unknown policy denied; set/version conflict; physical3EA at4kg/EA →12kg, box10kg →tolerance5; gross7 и17 проходят, ±0.000000001 снаружи границ не проходят; failed check revokes prior approval; mass edit/restore invalidates; scan/replay, mismatched quantity, edit-restore, pinned shipment and wave finish; P/H cleaned root. API OpenAPI и JS syntax подтверждены, browser не заявлен.

Ограничения: нормативная масса не заменяет фактические индивидуальные веса весового SKU. Для variable-weight/неполных коробок/другой реальной упаковки нужен подтверждённый физический mass/pack contract NI04.2/NI07.1; не объявлять full weight acceptance. Настройки по подскладу/магазину, освобождение целой monopal, независимые роли/выборка, marks/labels/overrides остаются отдельными tickets.

Slow SQL policy read1jn7ttj9zn77j ~3.65ms, metadata DDL introspection115–157ms вне hot path. Решение: bounded200 allocations, indexed existing ware/SKU key; новый индекс не требуется по этому case. Global CONFIG X остаётся NI08 scalability ticket.
