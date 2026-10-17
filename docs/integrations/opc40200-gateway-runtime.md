# Запуск OPC40200 клиента шлюза

Реализован отдельный read-only клиент **OPC 40200 v2.00** для участка весы → шлюз,
магазинная проекция в существующий capture API и отдельная доставка raw evidence.
Драйвер использует закреплённый `asyncua==2.1.0`. WMS API не требует установки
этой библиотеки: OPC modules не импортируются из API composition/public.
[Библиотека и выпуск](https://pypi.org/project/asyncua/2.1.0/),
[официальный клиентский API](https://opcua-asyncio.readthedocs.io/en/latest/api/asyncua.client.html).

## Установка и запуск

```powershell
python -m venv .venv-scale-gateway
.\.venv-scale-gateway\Scripts\python.exe -m pip install -r tools/requirements-scale-gateway.txt
.\.venv-scale-gateway\Scripts\python.exe tools/store_scale_opc_gateway.py --profile C:\ScaleConfig\store-17.json --runtime C:\ScaleData\store-17
```

Команда работает непрерывно; `--once` выполняет один цикл. Нормальный порядок:
запустить шлюз при пустой платформе → получить действительное нулевое наблюдение →
открыть запрос из приложения и поставить груз → дождаться реальной устойчивой серии.
Если процесс запущен уже с грузом и подтверждённого нуля нет, возвращается
`OPC_EMPTY_PLATFORM_ZERO_REQUIRED`, а не выдуманный нулевой timestamp.
После reconnect нужен новый ноль; он не восстанавливается из предыдущего процесса.

HTTPS identity поставщика задают `STORE_SCALE_API_ORIGIN`, `STORE_SCALE_SENDER`,
`STORE_SCALE_PASSWORD`. Это выделенный sender устройства, не приёмщик и не admin.
Закрытый ключ OPC может использовать пароль `STORE_SCALE_OPC_KEY_PASSWORD`.
Если OPC сервер требует UserName identity, задают оба `STORE_SCALE_OPC_USER` и
`STORE_SCALE_OPC_PASSWORD`; они передаются только после настройки шифрованного
SecureChannel. При их отсутствии применяется anonymous UserIdentity внутри
защищённого соединения с application certificate; такой read-only режим должен
быть явно допущен настройками сервера площадки. Клиент не настраивает серверные ACL.
Секреты не печатаются и не включаются в raw capture.

`--allow-loopback-http` разрешает HTTP только для локального тестового WMS API.
OPC клиент всегда требует **Basic256Sha256 / SignAndEncrypt** и закреплённый
сертификат сервера. Нет рабочего режима insecure OPC, авто-доверия или выбора
случайного endpoint через discovery. Другую security policy следует добавлять
отдельным проверенным профилем, без автоматического понижения защиты.

## Паспорт конкретной модели

JSON-файл содержит:

| Ключ | Значение из ввода оборудования |
|---|---|
| model_namespace_uri / model_version | `http://opcfoundation.org/UA/Scales/V2/`, `2.00` |
| endpoint | Реальный `opc.tcp://host:port/path`, с явным портом, без пароля в URL |
| device_id / station_id | Назначенные идентификаторы физического устройства/поста |
| application_uri / server_application_uri | Application URI клиента и ожидаемого сервера |
| security.client_certificate / private_key / server_certificate | Файлы сертификатов и ключа; пути относительно паспорта либо абсолютные |
| security.server_sha256 | SHA256 DER-сертификата сервера; не fingerprint сертификата клиента |
| security.revoked_sha256 | Опциональный список явно отозванных server fingerprints |
| unit_namespace_uri / kg_unit_id | Проверенная `EUInformation` единица KG из реальной модели |
| no_tare_mode | Проверенное значение режима без device tare для GROSS профиля |
| nodes | Ровно current_weight, stable, center_zero, overload, underload, tare_mode, engineering_units |

Каждый nodes item: `{ "namespace_uri": "URI из паспорта поставщика",
"identifier_type": "s", "identifier": "реальный String NodeId" }` либо
`identifier_type:"i"` с числовым identifier. Служба разрешает namespace index
по URI при каждом соединении. Numeric namespace indexes не копируют между весами.
Конкретные NodeIds здесь намеренно не предлагаются: их предоставляет реальная модель.
Поддержка Guid/ByteString NodeId ещё не реализована этим профилем.

Клиент проверяет namespace v2 и что current_weight имеет DataType с BrowseName
WeightType в этом namespace. Custom structured types загружаются из доверенного
OPC сервера. Gross/Net/Tare читаются из исходного WeightType, не из PrintableValue.
Отсутствующие обязательные mapping/WeightStable/CenterOfZero не подменяются константой.
Серверная готовность остальных разрешений, поверки и policy остаётся в WMS native.

Сертификат сервера проверяется по pin, Application URI, срокам и extended/key usage
через валидатор библиотеки. Отзыв из profile проверяется дополнительно. Полная
CA/CRL инфраструктура и распространение trust list площадки пока не реализованы;
сертификат нельзя автоматически обновить скачиванием с endpoint. На стороне
оборудования отдельно настраиваются доверие application certificate шлюза и
минимальные права пользователя/приложения: чтение нужных узлов без управления тарой.

## Какие наблюдения допускаются

Каждый цикл делает настоящий OPC UA Read с **MaxAge=0** и TimestampsToReturn=Both
для семи полей, не копирует одно уведомление в пять sample. Значение берётся из
DataValue, сохраняются исходные status/type/value/source/server timestamps.
[DataValue и времена](https://reference.opcfoundation.org/specs/OPC-10000-4/7.11).

Текущий строгий профиль принимает только Good с StatusCode=0, non-null value,
aware source/server timestamps. ServerTimestamp должен быть не старше3 секунд
и не впереди локального UTC более1 секунды; sourceTimestamp не позже server.
Старый source timestamp у постоянного веса допускается при свежем реальном Read
и server timestamp; он не переписывается. Эти требования предъявляются ко всем
семи выбранным узлам. Модель со статическими metadata timestamps или отсутствием
нужных времён требует отдельного проверенного профиля, не обхода проверки.

Stable/zero/overload/underload должны быть Boolean. Overload, underload, неверный
TareMode, ненулевая device tare, другая единица, NaN/Infinity или отрицательная
недопустимая масса блокируют capture. GROSS берётся напрямую; net/tare остаются
в evidence и не вычитаются из него повторно. Значения не округляются и не усредняются.
Физическая масса пустой коробки — отдельный предметный факт EMPTY_TARE, она не
равна device preset tare, которую этот магазинный профиль запрещает.

Окно собирается автоматически из положительных Stable наблюдений через500мс:
не менее5 samples и не менее2 секунд, не более25/10 секунд. Motion обрывает
незавершённое окно. Допустимость разброса/дискретности/capacity проверяет прежний
**RRL_SCALE_PACKET_READ**, второй алгоритм устойчивости не добавлен. Значение
measured_at берётся из реального server timestamp последнего weight Read;
zero_check_at — из реально сохранённого нулевого Read. Превышение таймаута не
подтверждает приёмку. Отдельная goods-to-person INCREMENTAL_ASSEMBLY цепочка
before/change/after и её stock effect этим store service не реализуются.

## Lease, outbox и evidence

`SqliteScaleDeviceLease` защищает физическое окно на одном gateway host:
исключительный token/expiry, renew до/после Read, устаревший token не может
продлить/освободить новую аренду. Все процессы одного физического поста обязаны
использовать одну runtime DB. Это **не распределённый claim между разными host**;
для нескольких независимых шлюзов нужен серверный station coordinator.

До HTTP отправки сохраняются исходные raw observations и канонический capture.
Для них отдельные SQLite outbox с fsync и неизменной device/capture identity;
raw имеет явный bound128KiB, старый store bound64KiB сохранён. Потерянный ответ
повторяет прежнее тело. Неизвестный/неверный ACK не превращается в успех.

Raw envelope соответствует `ScaleEvidence`: normalized Numeric/String NodeIds,
исходные7 DataValues, настоящее нулевое наблюдение,5–25 observations с offsets,
profile SHA и capture SHA, station/model и gateway-reported certificate identity.
Он отправляется отдельно в `/api/integrations/scale-evidence`; ответ сверяется с
canonical raw SHA и capture IDs/SHA, status ARCHIVED, binding PENDING/MATCHED,
provenance GATEWAY_REPORTED, stock_posted:false. PENDING не объявляется полным
business proof. Серверный raw archive не является независимой аттестацией того,
что отправитель прочитал именно указанные физические весы.

Сохранение capture и raw archive пока не атомарно и само не подтверждает магазинную
приёмку. Шлюз не делает stock write. Warehouse API DTO отличаются; нынешний service
производит STORE_RECEIPT пакет. Складской gateway projection и общая assembly
координация требуют соответствующего сценария, а не замены URL.

## Проверки и ограничения

Стенд поднимает настоящий локальный OPC UA server с SignAndEncrypt, реальными
сертификатами, custom WeightType v2 и TCP соединением. Проверены zero→capture,
качественные/временные/единичные отказы, preset/range, неправильный certificate pin,
reconnect и сброс zero, строгие текущие HTTP DTO, отдельная lease двух worker,
raw ACK и bounds. Это программный стенд; физическое оборудование/поверка/
аппаратная динамика/промышленная нагрузка не подтверждены.

```powershell
# Дополнительно установить pytest в gateway test venv:
.\.venv-scale-gateway\Scripts\python.exe -m pytest tests/retailcase/test_scale_opc_client.py tests/retailcase/test_scale_device_lease.py tests/retailcase/test_scale_evidence_delivery.py -q -p no:cacheprovider
```

Архитектурные и encoding проверки общие для репозитория. При подключении реальной
модели повторяются commissioning matrix из [общего описания](weighing-gateway-opc40200.md).

## Atomic local capture/evidence staging — 15.10.2026

Both OPC service launchers now use `<runtime>/bundles.sqlite`. A single SQLite transaction with `synchronous=FULL` stores the immutable capture body and raw evidence body together, keyed by kind/device/capture. The canonical capture digest in raw evidence must match the saved body. Original transport bytes are preserved even when their JSON whitespace differs from canonical hashing.

The bundle is committed while the physical-device lease is held. After acquiring that lease, the capture adapter checks the journal again and returns the original pair for an already saved identity without reading a new weight. The journal then mirrors both exact bodies into the existing capture/evidence outboxes. A crash after the bundle commit, after either mirror or before the mirror marker is recovered by exact-byte staging. Queue ACKs are independent and are never reset by reconciliation.

Every startup reconciles before OPC connection; every cycle reconciles before considering a new measurement. The runtime directory and shared physical lease DB must stay stable across restarts. Workers representing the same station must share those paths. The lease remains local to one host/shared SQLite filesystem; no distributed multi-host ownership is claimed. Do not delete or move journal/outbox files to clear an error.

Existing pre-bundle capture-only records continue their exact delivery; they are not remeasured. A legacy raw record without its original capture is blocked with `SCALE_LEGACY_RAW_NEEDS_RECONCILIATION` before OPC connection or HTTP delivery. Investigate original body/audit and reconcile with the exact original packet; a fresh weight or a new identity must not be substituted. Existing archives and ACK states are retained.

This is atomic **local staging**, not atomic HTTP delivery or a combined native capture/raw transaction. Native capture and raw evidence still have separate ACKs and raw may be PENDING until its capture archive exists. A process crash before a local bundle commit has no persisted accepted measurement; no physical measurement durability claim precedes that commit.

Verification: `test_scale_bundle_journal.py` has 13 fault/identity/concurrency/lease/ACK tests. Existing genuine encrypted local OPC store/assembly tests now persist bundles; reuse succeeds even after the server changes to Bad quality because no new read occurs for the saved ID. A separate real local HTTP cycle exercises bundle mirroring and both ACKs. These are protocol fixtures, not physical hardware acceptance.

