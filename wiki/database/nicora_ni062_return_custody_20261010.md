# NI06.2 — две подписи передачи возврата
Ticket095,10.10.2026. [Решение](nicora_ni062_return_custody_design_20261010.md), [SQL](../../db/migrations/2026-10-10_ni062_return_custody/apply.sql). Миграция 2026-10-10-095-store-return-custody APPLIED; три spec/body, guards и queue indexes VALID.

STORE_RETURN_HANDOVER: тот же текущий departed trip/driver/vehicle, исходный ordinary approval/SAP, существующая адресная связь receiver, фактическая паллета (включая внутренний идентификатор), полное original BASE quantity и actual gross ≤ planned. Первый slice только physical_places1; multi-place требует собственного подробного manifest. Подпись магазина оставляет custody STORE_PENDING_DRIVER.

STORE_RETURN_PICKUP: dedicated current active RUSERS driver binding, exact current trip driver, иной actor, scan vehicle/pallet, current conservative outbound+planned-return capacity и отсутствие другого LOADED trip. GLOBAL_ADMIN не выдаётся за связанного водителя. Подпись водителя создаёт custody VEHICLE. Warehouse P/H/events не меняется; actual warehouse receipt отдельно.

Transport owner хранит versioned RRL_TRANSPORT_DRIVER_USER через existing configuration fence и warehouse_settings_edit; driver/RUSERS legacy не имеют PK, новые фиктивные FK не создаются. Проверяются single active driver/user/right. Отключение вместо удаления. Административная страница [driver-bindings.html](../../wiki-raw/wms_admin_ui_reference/driver-bindings.html). Legacy anonymous driver_id endpoints не используются для этих writes.

API /api/delivery/store-return-custody, scoped store/driver queues bounded100+optional trip filter. DriverMobilePage содержит отдельный feature [ReturnCustodyPanel](../../admin/wms_admin_frontend/src/features/delivery/ReturnCustodyPanel.tsx): отдельные credentials, actual quantity/mass/place scan, две подписи, durable original intent/retry и source/user reset. Пароли не сохраняются в localStorage. Синхронный ref блокирует double-click до React render.

Actual author case: own SUPPLIER approval bea258a7dd/092–094, two real role users, existing driver binding. Quantity/mass excess, admin driver spoof, foreign scan, duplicate refused; exact replay passed. Internal pallet identifier accepted. Handover+pickup each outbox1/events0, immutable delete denied. Binding deactivated, own users retired; historical valid custody remains VEHICLE. Scoped queue route PASS. Frontend TypeScript PASS. Не independent acceptance.

Slow SQL queue66.067ms/store and55.073ms/driver first execution; insert16.743/15.381ms. Решение выполнено: store/TT/time and driver/TT indexes, push optional TT filter to bounded server read. Индексы live VALID; no global queue lock or stock scan.

Открыто: stock return receiving/placement, corrections/cancel/replan, multiple physical places, marked unit/regulatory lifecycle, historical driver-binding audit beyond API audit and pickup snapshot. Full NI06.2 remains in_progress.
