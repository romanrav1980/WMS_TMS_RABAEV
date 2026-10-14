# Исходники NI03.2 и владельцы

09.10.2026. [[../database/retailcase_ni032_task_recovery_20261009]] — фактический результат/ограничения; [[../requirements/retailcase_delivery_v55/execution/active/ni03_2]] — текущий состав.

| Область | Место | Ответственность |
|---|---|---|
| Ресурсы | [modules/resources](../../api/wms_api_server/app/modules/resources/) | Политика назначения, квалификации, наблюдаемая позиция, nearest dispatch, CASE handoff |
| Остатки и факт | [modules/inventory](../../api/wms_api_server/app/modules/inventory/) | Root stock posting, source eligibility, progress, scan evidence, shortage recovery |
| Композиция | [resource_composition.py](../../api/wms_api_server/app/resource_composition.py) | Внедряет существующий WarehouseTaskService как callable port; правила не копирует |
| CASE legacy facade | [case_pick_service.py](../../api/wms_api_server/app/services/case_pick_service.py) | Существующие чтения/стыки; новые actions делегируются public API предметных модулей |
| Oracle current core | [current_runtime_manifest.json](../../db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json) | Актуальные пакеты, исходники, required columns; единый executor |
| Версионные изменения | [db/migrations](../../db/migrations/) | 09.10.2026 NI03.1/NI03.2 folders, migrations007–018, согласованные apply/rollback/checkpoint |
| ARM/ТСД | [raw admin UI](../../wiki-raw/wms_admin_ui_reference/) | Существующие warehouse/CASE/inventory/resource страницы с отдельными recovery/scan/handoff/decimal scripts |
| Обработчик | [short_recovery_worker.py](../../scripts/short_recovery_worker.py) | Последовательная lease/frozen-intent обработка существующих документов |
| Lifecycle worker | [start](../../scripts/start-short-recovery.ps1), [stop](../../scripts/stop-short-recovery.ps1) | Hidden process, PID/start identity, штатный stop marker |
| Адресные случаи | [task](../../scripts/ni032_task_cases.py), [short](../../scripts/ni032_short_case.py), [partial source](../../scripts/ni032_partial_replenishment_case.py) | Собственные fixtures, ограниченный факт/отказы/replay, возврат своего stock через ядро |
| Независимые задания | [Qwen](../../задания%20на%20проведения%20тестов/NI03.2/README.md) | Роль проверяющего, сценарии и GAP; независимый запуск не заявлен |

Публичные зависимости идут через public.py. Новые resource actions не импортируют legacy CASE/Warehouse services обратно: исполнитель назначения внедряется из composition root. CASE event writer вынесен в inventory/infrastructure/case_events.py, сохраняя существующую таблицу и outer transaction.

Количество изменяет только RRL_STOCK_POSTING_API. Resource/meta операции не выполняют самостоятельных проводок. Read API/preview не означает резерв или физический факт. Маркировка берётся из WMS SKU/profile; код товара и уникальный код штуки различаются, несколько профилей не увеличивают физический запас.

Global architecture FAIL остаётся по прежним legacy/API зависимостям. Извлечение не означает устранения всего архитектурного долга или полного закрытия NI03.2. Новая таблица задач, новая TMS, новая схема RETAILCASE и второй Oracle не создавались.

Общий SOFT: inventory/domain/pool_allocation.py, pool_plan.py/pool_service.py и master_data allocation_policy.py. Consumer binding и mini/MAX: [[../database/retailcase_ni032_replenishment_lifecycle_20261009]], inventory/minimax_service.py, replenishment_composition.py и scripts/minimax_worker.py. Current migrations008–024 APPLIED; installation snapshots неизменны, current manifest задаёт актуальные пакеты.

## Новые стыки 032–039

- inventory: alternative_pick_faces, wave_commands (общий durable intent), wave_pick_release, partial_shipment_layout.
- fulfillment: execution_progress (физическое исполнение по строкам).
- Oracle: BASE shipment projection, shift/incident instants, pending recount source eligibility, wave picking admission, dynamic BASE volume.
- [Статус NI03.3](../database/retailcase_ni033_execution_20261009.md), [dynamic routing](../database/retailcase_ni032_alternative_faces_20261009.md).

## HU slices050–053

Inventory warehouse_hu/API routes; existing pallet IDs and versioned RRL_WMS_HU_LINK, stock HU read/cmd/task/slot, existing MANUAL/PUTAWAY/resource/sync. Existing ARM warehouse-hus and warehouse-tasks share durable posting. [[../database/retailcase_ni041_hu_slots_20261010]] includes current slot, SI dimensions and one top-place claim. Regulatory aggregation remains separate.
