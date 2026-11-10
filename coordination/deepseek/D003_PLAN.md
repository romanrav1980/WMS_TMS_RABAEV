# D003 — очередь разработки

Короткая очередь блоков; после каждого — переход к следующему без ожидания приёмки.

| # | Спринт/блок | Реальный пробел | Файлы | Статус |
|---|---|---|---|---|
| 1 | D001 (S4/13/29) | intent до POST; повтор по сохранённым params; отказ/восстановление; серверный operation_id | tripCreate.ts, TransportDispatchPage.tsx, clusterRetry.ts, schemas.py, transport_service.py, trip_edit.py, миграция | ✅ implemented_awaiting_validation (RESULT/D003-01, D003-03) |
| 2 | D002 (S8/10/101) | полный результат job_id; async solve/cancel; применение по исходному payload; index.ts | plannerRun.ts, TransportPlannerPage.tsx, transport.py, index.ts, useVehicleAvailability.ts | ✅ implemented_awaiting_validation (RESULT/D003-02, D003-04) |
| 3 | ТМС-2 release-gate | fixture рейса S11/13/20, ненулевой авто-план S8, Wave 3 registry | — (в основном verification) | ⏸ перенесено в D003_VALIDATION.md |
| 4 | TRADECASE внутренний | по tradecase_execution_20261019.md; проверить конфликты с Claude | api/wms_api_server, terminal | ⏳ далее |

Порядок: 4 (с проверкой конфликтов Claude). Live/Oracle DDL не применять; миграции готовить + передавать Codex списком.
