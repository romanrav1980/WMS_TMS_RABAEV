# Магазин: запрос взвешивания через API

MIGRATION_ID: `2026-10-15-store-scale-requests`. Статус: **APPLIED** root после ревью, 10 statements / 0 errors; live body совпадает с исходником, USER_ERRORS=0 / INVALID=0. Владелец подтвердил: модели весов выбираются позднее, обмен с сервером проходит через API. См. [[retailcase_ni053_scale_capture_20261010]], [[retailcase_store_app_strategies_20261015]].

## Граница

`RRL_STORE_WEIGH_REQUEST` — неизменяемое намерение измерить конкретную финальную поставку. Массы в запросе нет. Источник веса остаётся единственным: `RRL_STORE_SCALE_API.capture` → `RRL_STORE_SCALE_CAPTURE`. Ни запрос, ни архив измерения не подтверждают приёмку и не меняют запас.

Новый `RRL_STORE_WEIGH_API` проверяет актуального приёмщика через `require_receiver`, фактическое финальное плечо через `describe_load`, непринятую поставку, стратегию `WEIGHT_PHOTO`, состав и текущую версию правил. Устройство явно связано с адресом и отдельным действующим sender с `store_scale_ingest`; `GLOBAL_ADMIN` не назначается шлюзом. Состояние `READY` означает пригодность настройки и поверки. Состояние связи всегда `UNKNOWN`: отсутствие heartbeat не подменяется вымышленным онлайн.

## Протокол 1.0

Все маршруты принимают `X-Scale-Protocol-Version: 1.0`; неизвестная версия отклоняется до сервиса. Заголовок не меняет тело и hash исходного пакета оборудования.

- `GET /api/delivery/store-scales/devices?load_operation_id=…&store_address=…`: до 50 настроенных устройств, active, capacity/resolution как decimal string, поверка, readiness, connectivity.
- `POST /api/delivery/store-scales/requests`: ровно `request_id`, `device_id`, `load_operation_id`, `store_address`, `expected_composition_signature`. Масса и произвольный actor запрещены схемой.
- `GET /api/delivery/store-scales/requests/{request_id}`: текущий приёмщик и автор запроса; `REQUESTED`, `CAPTURED`, `EXPIRED`, `STALE`. `capture_key` выдаётся только для сопоставленного оригинального измерения.
- `GET /api/delivery/store-scales/gateway/requests?device_id=…`: отдельный sender конкретного устройства, максимум 20 ожидающих запросов.
- Шлюз измеряет и отправляет существующий `POST /api/delivery/store-scales/captures`, используя **`capture_id=request_id`**. После потери ответа повторяет неизменный исходный пакет с прежними device/capture ID.

Срок запроса — 120 секунд по серверным timestamps. Один активный ожидающий запрос на устройство; повтор точного тела и автора возвращает тот же запрос, другое тело конфликтует. Устройство сериализуется row lock, отзыв прав — `RRL_ACCESS_REV` SHARE. Блокировки ограничены `WAIT 2`; неизвестный результат возвращает 503 с прежним request_id для сверки/повтора. Запрос не обновляется для «завершения»: результат выводится из append-only архива измерений.

`CAPTURED` требует device/capture ID, фактические load/store, device policy/calibration, sender, measurement и server receive внутри интервала запроса. Текущий состав и правила должны совпадать с сохранёнными. Позднее/старое или чужое измерение не разрешает приёмку. Смена правил, состава, доступов либо завершённая приёмка дают `STALE`; после истечения без измерения — `EXPIRED`. Повтор истёкшего запроса не продлевает срок.

## Проверка и восстановление

[Миграция](../../db/migrations/2026-10-15_store_scale_requests/apply.sql): before/schema/body/verify/rollback/checkpoint. До применения выполнен read-only baseline: RABAEV/orcl, INVALID=0, имена новых объектов отсутствуют. После применения проверены точный body, отсутствие compile errors и глобальный INVALID=0; checkpoint обновлён до APPLIED.

[HTTP тесты](../../tests/retailcase/test_store_scale_requests.py): **15 PASS** — identity без admin grant, mass/actor injection, malformed identity, неизвестная версия, изоляция gateway и классификация потери ответа. Payload conflict не считается доказанным отклонением прежнего запроса: outcome_confirmed=false/read_before_retry=true. BUSY при новом намерении — подтверждённый отказ его создания, исходное активное намерение сохраняется.

[Native rollback smoke](../../scripts/store_scale_requests_native_smoke.py): **11 PASS** — isolated actors/device/policy и две пары request/capture в одной caller-owned транзакции; exact replay/conflict/busy/owner/sender/revoke, изменённый состав и измерение до начала запроса. Реальная квитанция `RRL_STORE_SCALE_API.capture` прошла валидатор ACK шлюза, включая compact UTF-8 identity hash и canonical source SHA. После rollback отсутствуют обе пары request/capture, устройство и тестовые пользователи. NativeAPI.post и товарная приёмка не вызывались.

[Live API](../../reports/retailcase/2026-10-15/store-app/scale-request-api.json): **6 PASS** — devices200, version422, missing request404, unknown device sender403, browser mass422, bad login401. Положительный native путь использует caller-owned rollback; положительный HTTP POST не оставлялся в неизменяемом журнале ради проверки транспорта. [Native evidence](../../reports/retailcase/2026-10-15/store-app/scale-request-native.json).

В первой синтетической попытке часы Windows отставали от Oracle: исходное измерение оказалось до начала запроса и правильно получило STALE. Тест использует Oracle UTC clock; производственный шлюз должен синхронизировать часы. Guard не ослаблялся. Физические весы и многосессионная гонка этим не доказаны; late-after-120s не исполняется ускоренной подменой immutable timestamps.

Rollback отказывается удалять непустую историю запросов. После реального использования сначала нужны экспорт и явное решение восстановления; штатная миграция не переписывает оригинальные capture/receipt.

SQL: [review](../../reports/retailcase/2026-10-15/store-app/scale-request-sql.json). RRL_SQL_SLOW_LOG4492–4498: полный rollback fixture 225–589ms, отрицательные API 10–16ms. Oracle top SQL: request insert avg7.709ms/6, device active window1.660ms/10, gateway pending1.477ms/8, PK status0.544ms/15. Решение: сохранить PK/device-expiry индекс и bounds20/21/50; нет измеренного основания для дополнительного индекса. Запрос не ждёт оборудования внутри Oracle. Многосессионный load test остаётся отдельной проверкой; индексы SYS/слепые индексы на legacy не добавлялись.
