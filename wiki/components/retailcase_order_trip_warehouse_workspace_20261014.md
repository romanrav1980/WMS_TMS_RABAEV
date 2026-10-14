# B01: заказ, существующий рейс и складское обеспечение
14.10.2026 /1221–1232.

Использован прежний trip_selector: дополнительный ASSIGN source context для unassigned ST, действующий scoped current_sources, исходные ID/date/hash,31day и keyset100. DEFER исходный scope сохранён. Источник hash используется для выбора; это не разрешение на проведение.

Customer orders использует прежнее окно фильтра даты/района/магазина, прежний TMS assign endpoint. Actual SAP_2135→33571/2старыхместа/repeat/P0H0; текущий TT/dock в существующем fulfillment read model, ссылка на loading и auth-aware trip_id deep link. Документы не становятся погруженными от назначения.

В том же заказе добавлено рабочее место существующих pick plans: read/create, обеспечение/недостача, переход к волнам своего склада. Existing native planner создан2187 NO_STOCK с36 потребности/0обеспечения/36недостачи/0issued tasks, без рождения товара. Пустой план предлагается отменить перед новым расчётом после появления запаса. Это не новый planner и не завершённая полная волна.

Legacy plan create не имеет operation_id; интерфейс сохраняет неизвестный запрос и не повторяет его автоматически. Архив после confirmed отказа требует чтения исходного заказа. Полноценный серверный idempotency contract legacy creation не добавлялся и не выдаётся за готовый.

[Отчёт41](../../reports/retailcase/2026-10-13/41-order-trip-warehouse-workspace-report.md), screenshots60–63. Gates/limits/SQL decision в отчёте; owner transport/inventory/fulfillment. Full B01 открытый: положительное обеспечение/склад/mixed CASE/QC/loading и сроки.
