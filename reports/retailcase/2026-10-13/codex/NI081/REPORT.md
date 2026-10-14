# NI08.1-R1 — результат

Готов native единый расчёт маршрута с отдыхом для preview и final approval, общий для ручного и автоматического назначения. Изменены только транспортные плановые механизмы; новый stock engine/solver/права/DDL таблиц не создавались.

- [Контракт и миграция](../../../../../wiki/database/retailcase_ni081_route_schedule_20261014.md).
- [Native cases](native_cases.json):9 ограниченных readonly случаев, включая150+90, REST, stale road, hard/soft windows,540, envelope, string ST.
- [Final approval](fixture.json): собственный TT33641, successful V6 write238.17мс → rollback/version0, old source после изменения own road отклонён. Setup committed, provider NI081TEST синтетический; без stock rows. Два неуспешных setup до commit откатились; их выделенные sequence ID не используются.
- [Browser](browser.json): actual React components из Vite в отдельном browser mount, реальные GET/native, ноль browser POST; это адресная проверка компонентов, не проход навигации всего диспетчера.
- [Скриншот](native_route.png).
- [SQL/runtime](runtime_sql.json): HTTP200/105мс; дорога39.197→6.882мс,2282→15buffers после bounded PK lookup hint; peer24.082мс. USER_ERRORS/INVALID пусты, ledger APPLIED.

## Изменённые runtime файлы

- transport/infrastructure/delivery_window_preview.py: native calculation; единые depot/age policy.
- transport/infrastructure/approved_schedule.py: adapter подтверждённых native segments для диагностики, факты сохраняются.
- transport/infrastructure/driver_day.py, time_preflight.py, coordination_preflight.py: использовать единое подтверждённое расписание, убрать уже закрытую оговорку о неучтённых перерывах.
- transport/domain/delivery_windows.py: удалён расходящийся Python-алгоритм.
- admin components/TransportDeliveryWindows.tsx: этапы и предупреждения.
- admin components/TransportTimeApproval.tsx: итоговое утверждение, подтверждение identity, readback pending, compare-before-delete.
- db/migrations/2026-10-14_ni081_route_rest_approval/: checkpoint, helper package, TimeAPI bodyV6, ledger, verify, rollback.

## Остаток

Обязательный кодовый gap NI08.1-R1 закрыт. Правовые нормы конкретных стран/режимов, внешняя занятость водителя, промышленная достоверность дорожного провайдера/часовых поясов и независимая приёмка остаются отдельными подтверждениями. Это не означает разрешение физического выезда. Общий architecture/encoding gate — ведущий, после объединения QC и этого блока. Не выполнены commit/push.
