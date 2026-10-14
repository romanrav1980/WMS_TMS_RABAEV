# NI06.3 — срок и долг магазина по таре, 099
Миграция2026-10-10-099-tare-return-deadlines APPLIED в RABAEV; RRL_STOCK_TARE_POLICY/CMD, view и guards VALID. Новые RETURN_POLICY/DELIVERY_POLICY, read-only RRL_TARE_STORE_DEBT. Root TARE_ACCEPT VEHICLE→STORE фиксирует политику вместе с движением баланса/подписью/журналом/outbox.

STORE имеет приоритет над CUSTOMER через точный действующий RRL_CUSTOMER_STORE_MAP.LEGACY_ADDR; несколько клиентов — отказ. SAME_DAY до следующей местной полуночи; DAYS до конца N-го дня после дня передачи; NEXT_DELIVERY при подтверждённой следующей товарной приёмке магазина другим рейсом. Часовой пояс задаётся явно. Новая магазинная передача без политики запрещена; прежние выдачи098 показывают UNCONFIGURED_LEGACY, политика не переносится назад.

FIFO долг рассчитан из immutable выдач и фактических возвратов STORE→VEHICLE по тому же owner/type/condition/store. Машина→склад не уменьшает магазин второй раз. Повреждения/списания пока отдельный следующий срез; долг не удаляется молча.

API: GET/PUT /api/inventory/tare/return-policy, GET warehouses/{id}/store-debt. Настройка через существующий CONFIG fence/warehouse_settings_edit/expected_version; snapshot immutable. Raw [настройка](../../wiki-raw/wms_admin_ui_reference/tare-return-policy.html), долг в tare-ledger и React inventory TarePanel. Тип/склад/магазин/клиент из действующих справочников.

## Фактическое подтверждение
Исходная задолженность2 — UNCONFIGURED_LEGACY. Новая фактическая выдача2 SAME_DAY snapshot1/Europe-Moscow. Изменение текущей политики на DAYS3/version2 не меняет сохранённый срок; exact Root replay проходит. Фактический возврат2 закрывает старые2 по FIFO, новая задолженность2/SAME_DAY остаётся; итогware4/store2/vehicle0, всего6. Изменение snapshot прямым DML запрещено. Own actors после сценария отключены.
[Первоначальный сценарий](../../scripts/ni063_tare_deadline_case.py) одноразовый; после ошибки SQL timezone был продолжен [исходный факт](../../scripts/ni063_tare_deadline_continue.py), без повторной выдачи2.

## Практические исправления
Oracle runtime AT TIME ZONE variable требует скобок: (v_tz). Thin oracledb не читает именованные TZ(DPY-3022): API выдаёт EFFECTIVE_DUE_AT как явный UTC ISO8601 через SQL to_char; регион хранится отдельно. Исторические данные и срок не изменялись для обхода драйвера.
Slow SQL: bounded debt query55.005мс, snapshot insert5.979, policycount1.935/PKread0.709. Сохранить индексы source/destination/store/type и window partitions owner/type/store для фильтрации. Владелец NI06.3: при росте объёма оценить план/pushdown, incremental read projection или пакетное вычисление; не хранить произвольную копию долга до доказанного узкого места.

NEXT_DELIVERY и CUSTOMER fallback реализованы, но отдельный независимый runtime сценарий ещё не пройден. Полный NI06.3 остаётся in_progress: повреждения/потери/претензии, пригодная тара в планировании, фактическая вместимость и независимая приёмка.
