# Складской OPC шлюз: запрос, claim и фактическое измерение

Реализован read-only OPC40200 v2.00 producer для текущих складских API. Он получает mass-free запрос оператора, сохраняет claim identity до HTTP, получает native claim, затем читает реальный ноль и GROSS серию. Сам шлюз не создаёт товарную операцию. Общая архитектура — [OPC gateway runtime](opc40200-gateway-runtime.md); native контракт — inventory/contracts_warehouse_scale_requests.py и migration2026-10-15_warehouse_scale_requests.

## Реализованный поток

```mermaid
sequenceDiagram
    participant O as Оператор / WMS
    participant N as Native API
    participant G as OPC шлюз
    participant L as Durable local journals
    participant S as OPC40200 весы
    O->>N: POST requests (сканы, purpose, version; без массы)
    G->>N: GET gateway/requests?device_id
    G->>L: Один request → неизменный claim_id и claim body
    G->>N: POST gateway/requests/{request}/claim
    N-->>G: CLAIMED, capture_context, claim_expires_at
    G->>S: Реальный пустой ноль после ACK
    G->>S: Поставить объект, новая stable GROSS серия
    G->>L: Одна SQLite TX: исходные capture + raw
    G->>N: Exact capture (claim_id = capture_id)
    G->>N: Exact raw1.0
```

Lease сервера30секунд, intent120секунд. Шлюз не придумывает claimed_at: API его не отдаёт. Все чтения начинаются после проверенного claim ACK; native сравнивает окно со своим CREATED_AT. Локально последние6секунд lease резервируются для доставки. Задержка сети всё равно может привести к native отказу первого позднего capture; historical exact ACK разбирается сервером отдельно.

Пустой ноль должен быть фактически увиден в этом claim: stable, center_zero и GROSS0, действительные DataValue и timestamps. Для полного контейнера потребуется безопасно снять его с платформы, дождаться нуля и вернуть для серии. Новое тарирование/SetZero/SetTare шлюз не вызывает. ASM initial tare, старый AFTER или записанный ноль другого запроса не заменяют этот факт.

## Поддерживаемый объём

- EMPTY_TARE и FINAL_GROSS — существующие CASE контейнеры, допускаемые native pallet type/final workflow. Это не новая универсальная функция взвешивания произвольной паллеты или машины при отгрузке. FINAL сохраняет настоящий tare_capture_key, контент и прежний owner QC.
- PICK — только GROSS пост с явно введённым в эксплуатацию паспортом `warehouse_pick_mode: "SEALED_WEIGHT_BOX"`. Это не преобразование GROSS в loose NET и не вычисление количества. Native owner подтверждает пригодность конкретного capture для весовой коробки.
- NET посты и PICK без такого commissioning mode явно отклоняются до claim/измерения. Поддержка реального NET профиля — отдельная будущая приёмка.

Старые WarehouseScalePacket/WarehouseFinalScalePacket и их canonical bytes не меняются. EMPTY_TARE/FINAL используют raw1.0 WAREHOUSE_FINAL, PICK — raw1.0 WAREHOUSE_PICK. Дополнительные поля в старые packet DTO не добавляются. Raw содержит реальные семь DataValue и отдельное zero_observation, остаётся gateway-reported evidence.

## Запуск

```powershell
.\tmp\scale-gateway-venv\Scripts\python.exe tools/warehouse_scale_opc_gateway.py --profile C:\ScaleConfig\opc-post.json --station-profile C:\ScaleConfig\warehouse-post.json --runtime C:\ScaleData\warehouse-post --lease-db C:\ScaleData\opc-device-leases.sqlite
```

OPC паспорт соответствует общей инструкции: актуальные реальные NodeId mappings, сертификаты и pin, URI/version2.00, реальные units/no-tare mapping. `--station-profile` — WarehouseGatewayProfile: device_id, warehouse_id, post_cell, device_mode(TEST/HARDWARE), device_policy_version, calibration_ref, basis(GROSS). Два паспорта должны указывать одно устройство. Для принятого sealed PICK mode поле добавляется именно в OPC паспорт, поэтому входит в его digest. Никаких реальных моделей/NodeId здесь не предполагается.

HTTPS credentials dedicated sender читаются из STORE_SCALE_API_ORIGIN/STORE_SCALE_SENDER/STORE_SCALE_PASSWORD, не печатаются. Учётная запись имеет warehouse_scale_ingest и текущее назначение устройства; это не оператор. Разрешённый loopback HTTP — только явный `--allow-loopback-http` для TEST. `--once` выполняет один цикл. Обычный Python может показать --help без asyncua; для измерений нужен pinned tool venv из общего runtime guide.

Все store/assembly/warehouse CLIs должны использовать один абсолютный lease DB физического поста и защищённый каталог runtime службы. Все экземпляры одной warehouse станции разделяют её claims/bundles/outboxes. Native claim дополнительно ограждает удалённые экземпляры; локальный SQLite lease не объявляется распределённой блокировкой.

## Сбой и границы восстановления

Перед OPC connection и каждым новым измерением восстанавливаются пары bundle → outbound queues и отправляются прежние тела. PENDING/SENDING, включая backoff, блокируют новое измерение до разрешения предыдущей доставки. После local bundle commit любой crash, в том числе между двумя mirrors, восстанавливает оба исходных тела без повторного измерения. Capture и raw имеют независимые ACK, атомарного HTTP/business commit не заявляется.

Lost claim ACK повторяет исходный claim_id/body. Один request получает одну identity в этом increment. Expired/inactive claim становится terminal diagnostic; новое ID и повторное измерение автоматически не создаются. Другой будущий request получает собственную identity. Неподтверждённый claim не доказывается отсутствием HTTP ответа.

Permanent capture/raw отказ сохраняет SUSPENDED и показывает SUSPENDED_ARCHIVES_REVIEW_REQUIRED; такая терминальная история не блокирует все будущие unrelated requests. Старый capture_id не переизмеряется и body не меняется. Старый dangling raw без capture означает NEEDS_RECONCILIATION, а не молчаливое снятие BLOCKED. Автоматический второй claim после expiry (native допускает максимум5) пока не реализован: owner integrations должен добавить доказательство отсутствия архива/исходной in-flight команды, отдельный новый claim под native fences и аудит разрешения. Непроверенные записи не удаляются вручную ради продолжения.

## Проверка

22 новых unit/fault/HTTP сценария: lost claim ACK/restart, два локальных исполнителя, expired claim, неправильный context/identity, старое окно, GROSS/NET commissioning guard, настоящий zero flag, crash после bundle commit/между mirrors, backoff drain и terminal history. Shared regression suite81 PASS.

Три encrypted localhost OPC→реальный loopback HTTP сценария (EMPTY_TARE/FINAL_GROSS/sealed PICK) прошли реальные cert/channel/7 DataValue, actual zero→replacement→series, request/claim paths, canonical старый DTO/raw1.0 и строгие отдельные ACK. Это моделируемый HTTP сервер и локальный OPC server, не реальные весы, не live Oracle и не аппаратная готовность. Native fixture приёмку владелец организует отдельно после применения backend kit.

## Реальный API/native стык EMPTY_TARE

15.10.2026 по отдельному разрешению root выполнен только EMPTY_TARE для CASE1136: production operator request→native claim→encrypted localhost OPC actual zero→поставленная TEST тара0.5→existing capture ARCHIVED→raw1.0 MATCHED. Использован именно новый OpcWarehouseCapture/claim journal/bundle/outboxes, actual profile/7DataValue и прежний dedicated sender, без изменения device policy. SourceP24/H1/version10 и CASE остались прежними. [Отчёт](../../reports/retailcase/2026-10-15/warehouse-weigh-request/opc-empty-native-http.json), [driver](../../scripts/warehouse_opc_native1136_empty.py).

Это реальный WMS HTTP/Oracle стык с локальным шифрованным OPC TEST сервером, не физические весы. Native FINAL_GROSS/sealed PICK этим проходом не подтверждены. Driver удерживает тот же TEST server/profile по ограниченному времени для отдельно разрешённых дальнейших клиентов; он сам не отправляет ASM BEFORE/AFTER, consent или товарную команду. Не запускать повторно и не менять fixture mass без текущего разрешения владельца.
