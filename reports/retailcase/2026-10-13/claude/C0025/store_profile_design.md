# Справочник магазинов, этап B — проект расширенного профиля (DDL не применялся)

14.10.2026 · Claude Code по поручению владельца и согласованию Codex C-0026: только проект, без DDL.

## 1. Что уже есть и остаётся единственным источником

Новый профиль эти поля не копирует, а читает рядом с ними (этап A, `/api/master-data/stores/card`).

| Параметр магазина | Существующий владелец |
|---|---|
| Адрес-ключ, регион/район/направление, порядок | `RRL_ADDR.ADDR`, `REGION`, `RAION`, `NAPR`, `ORD` |
| Координаты и радиус геозоны | `RRL_ADDR.SHIROTA`, `DOLGOTA`, `GEO_FENCE_RADIUS_M` |
| Тип ТС, максимальный тоннаж, стол-лифт | `RRL_ADDR.TRANSPORT_TYPE`, `MAX_VEHICLE_TONS`, `STOL` |
| Время отгрузки, срок выполнения, ворота по умолчанию, резерв | `RRL_ADDR.SHIPPING_TIME`, `LEAD_TIME`, `DOCK_DEFAULT`, `RESERVATION_ORDER` |
| Норма разгрузки (мин), признак строгого окна | `RRL_ADDR.UNLOAD_NORM_MIN`, `TW_STRICT` (только флаг, без границ окна) |
| Примечания, e-mail, группа клиента | `RRL_ADDR.PRIM1`, `PRIM2`, `EMAIL`, `CLIENT_GROUP` |
| Режим приёмки (штрихкод или вес+фото) | `RRL_STORE_RECEIPT_POLICY` (версии) |
| Получатели магазина | `RRL_STORE_RECEIPT_USER` |
| Срок возврата тары | `RRL_TARE_RETURN_POLICY` (`SCOPE_KIND=STORE`) |
| Код ERP, GLN, EDI | `RRL_CUSTOMER_STORE_MAP` |
| Дни поставок по складу, исключения | `RRL_SAP_STORE_CALENDAR`, `RRL_SAP_STORE_CAL_EXCEPTION` |
| Ёмкость адреса клиента (паллеты, вес, объём) | `RRL_CUSTOMER_ADDRESS` (клиентский адрес, связь с `ADDR` не прямая — см. п. 4) |

## 2. Чего нет — реальный остаток

1. **Окна приёма по дням недели** (с/по, несколько интервалов, перерыв). Сейчас есть только `TW_STRICT` без границ и `SHIPPING_TIME` — время отгрузки со склада, а не окно магазина.
2. **Подсобка:** есть или нет, вместимость в паллетах и ролл-кейджах, можно ли оставить товар без получателя, условия хранения (холод/заморозка).
3. **Подъезд и разгрузка:**
   - рампа, высота рампы;
   - ограничения ТС по высоте и длине на подъезде (сейчас есть только тоннаж);
   - способ разгрузки по умолчанию: паллета, ролл, вручную;
   - нужен ли грузчик.
4. **Контакт для приёмки** (роль, телефон) и инструкция доступа (въезд, пропуск, код).
5. **Временные ограничения** с датами действия (ремонт, закрытие), не связанные с календарём поставок SAP.

## 3. Предлагаемая схема (DDL — решение Codex)

- **`RRL_STORE_PROFILE`** — текущая версия; ключ `STORE_ADDR` — строка, как `RRL_ADDR.ADDR`, FK на `RRL_ADDR`.
  - Поля: `PROFILE_VERSION`, `BACKROOM_FLAG`, `BACKROOM_PALLETS`, `BACKROOM_ROLLS`, `UNATTENDED_DROP_FLAG`, `STORAGE_TEMP_CLASS`, `RAMP_FLAG`, `RAMP_HEIGHT_MM`, `MAX_VEHICLE_HEIGHT_MM`, `MAX_VEHICLE_LENGTH_MM`, `DEFAULT_UNLOAD_METHOD` (`PALLET`/`ROLL_CAGE`/`MANUAL` — как в `UnloadingDetails`), `LOADER_REQUIRED`, `CONTACT_ROLE`, `CONTACT_PHONE`, `ACCESS_NOTE`, `CHANGED_BY`, `CHANGED_AT`, `OPERATION_ID`, `PAYLOAD_HASH`.
- **`RRL_STORE_RECEIVING_WINDOW`** — строки окон: `STORE_ADDR`, `PROFILE_VERSION`, `WEEKDAY` (1–7), `FROM_MINUTE`, `TO_MINUTE`, `TIMEZONE_REGION`.
  - Проверки: `FROM < TO` и нет пересечений внутри дня.
- **`RRL_STORE_PROFILE_HIST`** — неизменяемая история версий (JSON и основание).
- **`RRL_STORE_RESTRICTION`** — временное ограничение: `VALID_FROM`, `VALID_TO`, `KIND`, `REASON`, версия.
- **Запись** — одна команда `STORE_PROFILE_SET`:
  - поля: `operation_id`, `expected_version`, `reason`;
  - идемпотентна по `OPERATION_ID` + `PAYLOAD_HASH`;
  - право `warehouse_settings_edit`;
  - товар не меняет.
- **Чтение** — тот же `/stores/card`, поле `profile_extensions`: сейчас `null`, после DDL — профиль, окна и действующие ограничения.

## 4. Открытые вопросы владельцу и Codex

- **`RRL_CUSTOMER_ADDRESS` и `RRL_ADDR`:** связаны ли через `RRL_CUSTOMER_STORE_MAP.LEGACY_ADDR`? Если да, ёмкость адреса показываем оттуда и в профиль не дублируем.
- **Флаг `TW_STRICT`:** остаётся «жёсткостью» окна, а сами границы переходят в `RRL_STORE_RECEIVING_WINDOW`. Нужно решить, читает ли VRP-планировщик эти окна — это зона Codex/transport.
- **Источник окон:** вводятся ли окна в WMS или приходят из ERP. При ERP-источнике WMS-ввод отключается, остаётся только чтение.
