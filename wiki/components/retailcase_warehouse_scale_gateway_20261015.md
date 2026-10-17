# Складской HTTPS adapter весов · 15.10.2026

Инкремент AK06-C: integrations получает отдельный складской HTTP adapter и durable exact-body delivery для существующих inventory архивов. Магазинный DTO/worker не перенаправляется в другой URL. Oracle/API/stock writer этим инкрементом не изменяются.

## Реализовано

`HttpWarehouseScaleGateway` использует существующий защищённый transport (HTTPS, проверка сертификата стандартным trust store, запрет redirect, dedicated Basic sender, timeout/response bounds) и выбирает `/api/inventory/warehouse-scales/captures` для PICK либо `/final-captures` для EMPTY_TARE/FINAL_GROSS. Перед отправкой применяется настоящий публичный inventory DTO; магазинные поля, неизвестные поля, неправильные типы и oversized body отвергаются. Складские sample имеют `weight_kg`, а не магазинный `gross_weight_kg`.

`WarehouseGatewayProfile` содержит зарегистрированные device_id/warehouse_id/post_cell/device_mode/device_policy_version/calibration_ref/basis. Новый packet сверяется с профилем и native сроком первой отправки (не старше30сек, не более2сек в будущем). Физические zero/sample/gross/tare и коды сканирования приходят из настоящего устройства/штатного контекста; adapter их не синтезирует и не заполняет массой из плана.

Повтор использует прежние bytes/device_id/capture_id в `SqliteScaleOutbox`: FULL synchronous, атомарный lease30сек, restart recovery, backoff, permanent rejection→SUSPENDED. Один capture_id не может поменять тело или purpose. Истечение срока нового замера не удаляет уже отправленную команду: exact retry после потери ответа идёт в native replay. Сохранённый оригинал сохраняет также прежние policy/calibration после перенастройки; сервер решает текущий допуск и существование исходного архива. Смена устройства/поста/basis профиля не позволяет отправить чужую очередь. Для магазина и каждого складского поста нужны отдельные outbox файлы.

ACK сверяет device/capture key, canonical source SHA256 (так же сериализует inventory service), склад/пост/mode/policy/calibration, CASE/task/line/content version, физические сканы, purpose/EMPTY_TARE reference, последнее измерение (не среднее), число и span samples. FINAL_GROSS дополнительно проверяет форму composition signature и согласованность gross/tare/net. ACK обязан иметь ARCHIVED и stock_posted=false; он не выдаёт QC/stock/receiving admission. Некорректный ACK сохраняет очередь для exact retry.

## Запуск

[CLI](../../tools/warehouse_scale_gateway.py):

```powershell
python tools/warehouse_scale_gateway.py --once --profile C:\station\warehouse-profile.json --packet-file C:\station\actual-capture.json --outbox C:\station\warehouse-scale.sqlite
```

Origin/identity берутся из `WAREHOUSE_SCALE_API_ORIGIN`, `WAREHOUSE_SCALE_SENDER`, `WAREHOUSE_SCALE_PASSWORD`; секреты не входят в profile и не выводятся. Profile должен соответствовать действительной регистрации warehouse device, а packet-file — содержать реальные наблюдения и существующий CASE/сканы. Без packet-file выполняется только повтор уже сохранённой очереди. `--allow-loopback-http` допускается для localhost dev, удалённый HTTP запрещён. Команда `--help` проверена. Это одноразовый delivery cycle, не служба установщика.

## Доказательства и границы

[20 focused tests](../../tests/retailcase/test_warehouse_scale_gateway.py): настоящий loopback HTTP для трёх purposes, потеря ответа/рестарт/повтор после TTL, ошибочные ACK, разные тела одной identity, expired first packet, магазинный DTO, HTTP302/401/409/503 и запрет переноса credentials по redirect. Данные этих unit-протокольных тестов не объявляются измерением оборудования.

[Native smoke](../../scripts/warehouse_gateway_native_smoke.py), [отчёт](../../reports/retailcase/2026-10-15/warehouse-scale-gateway/native-ack.json): настоящие существующие TEST архивы PICK/EMPTY_TARE/FINAL_GROSS приняты валидатором; RRL_WH_SCALE_API.capture возвращает побайтно прежний ACK при точном replay и отвергает изменённое тело той же identity. Caller rollback, число архивных строк не изменилось, новых измерений/товарных команд/commit нет. Это cross-proof текущего контракта, не физический пилот. Глобально INVALID0. После прогона slow log за час пуст; сохраняются прежние unique capture/device lookup, предположительных индексов нет. При повторяющемся >1000мс запросе требуется атрибуция/план, owner integrations/Codex. Native прямой тест не создавал HTTP API audit.

Architecture PASS953/затем957 файлов, 0циклов/72 прежних долга; общий gate проверяет root вместе с параллельными изменениями. Инкремент не реализует складской request/claim handshake, автоматическую OPC→warehouse-context проекцию и операторскую навигацию. OPC-client соседнего инкремента подключается через явный складской контекст; нельзя дать terminal вводить OPC NodeId или массу. SHIPPING_GROSS целой паллеты и INCREMENTAL_ASSEMBLY — отдельные предметные контракты, не режимы данного FINAL_GROSS. Сертификаты, настоящие весы/поверка и независимый физический пилот остаются открытыми.

[[architecture/retailcase_resource_gantt_shift_supervisor]], [[roadmap/retailcase_access_knowledge_plan]].
