# NI02.2 — температурные возможности автомобиля
Миграция: 2026-10-14-1149-vehicle-temperature-profile. Применена в RABAEV/orcl;2 statements/0errors, пакетVALID/USER_ERRORS empty/ledgerAPPLIED.

Существующий RRL_VEHICLE_PROFILE_API расширяется необязательной парой temp_min_c/temp_max_c (десятичные строки в °C). Оба предела и действующее основание обязательны, min≤max. Это заявленные возможности одного общего температурного пространства. Фактическое измерение, настройка холодильника и допуск погрузки отдельны.

Новая версия проходит прежнюю CONFIG fence, transport_fleet_edit, текущую версию и base_hash. Диапазон хранится внутри неизменяемого RESULT_JSON существующего RRL_VEHICLE_PROFILE_HIST; новых таблиц, колонок, quantity writer нет. Старые запросы/профили/хеши/история остаются совместимыми. Профиль без диапазона — неизвестный, BASE_CHANGED не допускает использовать его как подтверждённый.

Preflight читает текущий профиль в том же READ ONLY снимке с требованиями SKU. Точное пересечение диапазона возможностей машины с требованиями товара показывает достижимый диапазон. Это не проверка включения всего диапазона машины внутрь товарного диапазона. Нет общего режима/неизвестный SKU/машина — явный отказ подтверждения температурной совместимости. Measurement/operational admission остаются false.

Снимок исходного тела/спецификации и baseline INVALID: [checkpoint](../../db/migrations/2026-10-14_ni022_vehicle_temperature/checkpoint.json). Apply/rollback/verify рядом. Пакетный откат сохраняет историю JSON, не изменяет остатки. Разрешение владельца: продолжать реализацию всех спринтов в выделенном dev RABAEV.

1152/1157: private10100/v1, native negative decimal normalization, same-op two senders one result, changed body conflict, v2 outer rollback; protectedP20H20. Exact shared feasible2..6.25 against machine−20.125..6.25 andgoods2..8; incompatible/BASE_CHANGED/missingrange remainunconfirmed. Existing33571/SAP_2135 unknownSKU retained. TypeScript PASS, realdesktop45/mobile46; report34. SQL1.097ms4.5buffers/4.825ms62.5/2.659ms13; retainexisting keys/config fence/bounded one-row read, noindex, ownertransport. Physical observation and locked loading/departure thermal admission next; allfullsprints notclosed.
