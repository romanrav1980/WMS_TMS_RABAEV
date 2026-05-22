# Session Brief — [Название фазы]

> Скопируй этот шаблон, заполни три блока, вставь в начало сессии с Claude Code.

---

## Что уже есть

**Активная фаза:** [например: Transport Phase 2.1 — Кластеры на панели]

**Ключевые файлы:**
- `api/wms_api_server/app/services/transport_service.py` — [что там сейчас]
- `api/wms_api_server/app/routers/transport.py` — [текущие эндпоинты]
- `admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx` — [текущее поведение]

**Последний коммит фазы:** `_______` — [описание]

**Текущее поведение:** [1–2 предложения что уже работает в UI/API]

---

## Что добавить

**Один эндпоинт или один компонент** (не смешивать):

```
[HTTP метод + URL]
Request: { ... }
Response: { ... }
```

или

```
Компонент: [имя]
Props: { ... }
Поведение: [1–3 пункта]
```

**Порядок реализации в сессии:**
1. SQL/схема (если нужна миграция или новая Pydantic-модель)
2. Сервис (`transport_service.py`)
3. Роутер (`transport.py` + `schemas.py`)
4. Компонент (`.tsx` + `styles.css`)

---

## Как проверить

1. [Конкретное действие в UI или curl-запрос] → ожидаемый результат
2. [Граничный случай] → ожидаемое поведение
3. [Что не должно сломаться] → проверка регрессии

---

## Не делать в эту сессию

- [Например: не трогать биллинг, не рефакторить CreateTaskModal]

---

_Execution plan: [wiki/roadmap/transport_execution_plan.md](../roadmap/transport_execution_plan.md)_
