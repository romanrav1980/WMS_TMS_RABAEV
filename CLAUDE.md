# TMS — Project Guide for Claude Code

## Stack

| Слой | Технология |
|------|-----------|
| DB | Oracle 11g, схема `RABAEV`, JDBC через `cx_Oracle` |
| Backend | Python 3.11, FastAPI, `cx_Oracle`, Pydantic v2 |
| Frontend | React 19, TypeScript, Vite, plain CSS (никаких UI-библиотек) |
| Legacy | C# WinForms 4.7.2 — работает параллельно, не трогать |

## Структура папок

```
api/wms_api_server/app/
  routers/          ← FastAPI роутеры (один файл = один домен)
  services/         ← бизнес-логика + SQL
  schemas.py        ← все Pydantic-модели
  auth.py           ← permissions, get_current_user

admin/wms_admin_frontend/src/
  components/       ← страницы и крупные компоненты
  styles.css        ← единый файл стилей

db/migrations/      ← папка на каждый набор изменений, нумерация NNN_apply.sql

wiki/
  requirements/     ← ТЗ по модулям
  roadmap/          ← roadmap и execution plan
  templates/        ← шаблоны для сессий
```

## Активная работа

**Текущая фаза:** Transport Phase 2.1 — «Кластеры на панели»

Execution plan: [wiki/roadmap/transport_execution_plan.md](wiki/roadmap/transport_execution_plan.md)

## Ключевые файлы транспортного модуля

| Файл | Назначение |
|------|-----------|
| `api/wms_api_server/app/services/transport_service.py` | весь backend-сервис |
| `api/wms_api_server/app/routers/transport.py` | 15 эндпоинтов `/api/admin/transport/` |
| `admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx` | весь UI диспетчера |
| `db/migrations/2026-05-21_transport_dispatch_phase1/042_apply.sql` | вьюха RRL_V_AVAILABLE_STS |
| `db/migrations/2026-05-22_transport_dispatch_improvements/043_apply.sql` | +VERIFY_PERC, +NAPR |
| `wiki/requirements/transport_dispatch_tz.md` | полное ТЗ Phase 1 + 9 улучшений |
| `wiki/requirements/transport_billing_tz.md` | ТЗ биллинга |
| `wiki/roadmap/transport_roadmap.md` | roadmap Phase 2→3→Billing |

## Архитектурные правила

- Все мутации данных — только через Oracle-пакеты (`RRL_TRASPORT_TASK_ADD`, `RRL_TT_ADD_PALL`, `RRL_TT_REORDER_ADR`, `RRL_TT_SET_TRANSCOMMENT`). Прямой INSERT/UPDATE запрещён.
- C# WinForms продолжает работать параллельно — не менять Oracle-объекты, от которых он зависит.
- Единица назначения в рейс — **СТ** (сборочное задание, `ST_NUMBER`), не паллета.
- Проверка перед закрытием рейса: `TRANSPORT_TASK.can_print()` — если не 'ok', вернуть 422 с деталью.
- Права: `TRANSPORT_DISPATCH_VIEW`, `TRANSPORT_DISPATCH_EDIT`, `TRANSPORT_DISPATCH_CLOSE`, `send_empty_truck` (bypass can_print).
- Следующий номер миграции: **044**.

## Coding conventions

- Комментарии только когда WHY неочевиден (скрытое ограничение, обход бага Oracle).
- `ware_ids` в FastAPI — `Annotated[list[int] | None, Query()]`.
- CSS — только в `styles.css`, без inline-стилей и CSS-модулей.
- Новые Pydantic-схемы — только в `schemas.py`.
- Каждая sub-фаза = один коммит с хэшем в execution plan.
