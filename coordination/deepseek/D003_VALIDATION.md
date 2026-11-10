# D003 — очередь проверок (общий этап отладки)

Прогоны отложены по поручению владельца («сначала разработка, затем общий этап отладки»). Здесь фиксируются проверки для общего этапа; они не заменяют разработку.

## Статические (уже выполнены в блоке 1/2)
- `tsc --noEmit -p admin/wms_admin_frontend/tsconfig.json` → exit 0.
- `python -m py_compile` изменённых backend-файлов → exit 0.
- `check-encoding.ps1` → passed.

## ТМС-2 release gate (из transport_execution_plan.md, «Повторный release gate — 2026-10-29»)
- Fixture рейса для Sprint 11/13/20 (fixture операций/доступности/биллинга).
- Ненулевой авто-план Sprint 8 (fixture с геокодированными СТ и активным ТС).
- Обновление Wave 3 registry (тестовый реестр после модульного выделения driver/tariff/geofence).
- Команда: `pytest tests/transport/...` на стабильном seed; браузерные smoke; live — только по отдельному поручению.

## Live/Oracle (выполнено 29.10)
- Миграция `2026-10-29_transport_trip_create_idempotent` — **ПРИМЕНЕНА** и проверена: объекты VALID; тот же operation_id → тот же task_id; изменённый payload → конфликт. Откат — `001_rollback.sql`.

## Live/Oracle (осталось)
- `GET /planner/solve/{job_id}` + async SSE/cancel: live-прогон отмены, потери соединения, таймаута.

## Не запускать сейчас
- Полные регрессии, нагрузку, браузерные марафоны, live бизнес-операции (по поручению владельца).
