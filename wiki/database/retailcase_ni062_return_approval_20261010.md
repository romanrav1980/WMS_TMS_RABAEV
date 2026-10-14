# NI06.2 — согласование возврата Supply Chain
Ticket092, 10.10.2026. [Решение](retailcase_ni062_return_approval_design_20261010.md), [SQL](../../db/migrations/2026-10-10_ni062_return_approval/apply.sql). Миграция 2026-10-10-092-store-return-approval APPLIED в RABAEV; command/root spec/body и guard VALID.

STORE_RETURN_APPROVE сохраняет исходную приёмку/строку, SKU/lot/BASE/количество, причину и ссылку на решение Supply Chain, назначение REUSE/SUPPLIER/DISPOSAL. REUSE требует заявления о полной исправной коробке; фактическая проверка коробки остаётся обязанностью приёмки. Источник только фактически ACCEPTED quantity, missing/excess не увеличивают лимит. Маркированный состав пока отказывается до реализации unit allocation.

Общий Root блокирует исходную строку и новое разрешение в едином порядке, повторно проверяет cumulative cap; разрешение и outbox атомарны. История immutable. Состояние WAITING_SAP_AND_LOGISTICS, sap_verified=false. Разрешение не создаёт P/H, движения или государственного ACK. Не подменяет SAP-документ возврата закупкой.

API /api/delivery/store-returns/{receipt}/approve и bounded исходное досье; ARM [store-returns.html](../../wiki-raw/wms_admin_ui_reference/store-returns.html) с правом store_return_approve. Exact pending ID/body сохраняются до отправки; неопределённый ответ повторяется, смена пользователя очищает досье.

Фактический авторский case: accepted2 исходного bea258a7dd разрешены1 REUSE+1 SUPPLIER; лишнее количество, отсутствующая строка и неполная коробка отказали; replay/conflict/append guard прошли. P0/events0/outbox1. Конкурентные команды2+2 на accepted3 исходного04633c677f: одна APPLIED2, другая definitive409, суммарно2 и ноль outbox проигравшей команды. Не повторять эти сценарии на уже использованных лимитах.

Slow SQL: source dossier22.460ms, insert8.954ms average, cumulative3.225ms. Решение — индекс receipt/line, PK и bounds200lines/100history; сохранить локальную исходную блокировку, не блокировать весь магазин. Мощность не подтверждена.

Следующий стык: логистическое поручение существующему рейсу, подтверждённый SAP-return reference и физическая приёмка/размещение. Обычный declared box пока не считается измеренной/осмотренной. Полный NI06.2 остаётся in_progress.
