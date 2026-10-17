# OPC шлюз сборки: BEFORE и AFTER

Клиент реализует фактический [Assembly API v1](../../coordination/retailcase-claude/ASSEMBLY_SCALE_API_V1.md)
и использует общий read-only OPC40200 клиент и физический lease. Он не переиспользует
магазинный capture DTO, не подменяет серверный consent и не проводит остатки сам.
Активация native/API и приёмка бизнес-эффекта находятся у владельца inventory;
локальные OPC/HTTP тесты клиента не являются их заменой.

## Последовательность

1. Терминал открывает session с настоящим EMPTY_TARE и физическим сканом тары.
2. Оператор сканирует строку/товар/источник, задаёт количество и подтверждает
   consent для AUTO, если такой режим настроен на посту. Сервер заранее сохраняет
   step_id, operation_id и две capture identity.
3. Gateway читает `/api/inventory/assembly-scale/gateway/requests?device_id=…`.
   Для WAITING_BEFORE приходит BEFORE: собирается свежая серия реальных GROSS Read
   и передаётся в `/captures`. Native проверяет исходное плато и переводит шаг в ARMED.
4. Для AUTO сервер затем выдаёт AFTER. Gateway ждёт фактического изменения относительно
   `expected_before_kg` не менее серверного `min_delta_kg`, после него новую устойчивую
   серию. Исходное неизменное плато не принимается за укладку. Изменение в неверную
   сторону не исправляется в клиенте: native проверяет реальную delta и условия шага.
5. Для BUTTON сервер выдаёт AFTER только после `/steps/{step_id}/placed` от оператора.
   Gateway эту команду не вызывает. Если физическое изменение уже произошло до
   нажатия, фиксируется свежая реальная AFTER серия из текущего открытого контекста.
6. Hardware archive ACK не равен APPLIED. Сервер отдельно применяет сохранённый
   consent и единственную штатную CASE команду; UI читает фактический state шага.

В сборке тара остаётся на платформе. Новый ноль не запрашивается перед каждой
укладкой; SetZero/SetTare и вычитание прошлой массы из GROSS не выполняются.
Шлюз не превращает weight delta в количество самостоятельно. BEFORE/AFTER capture
содержит полные GROSS samples, а delta/допуск/товар/stock effect определяет native.
Для завершения сборки нужен отдельный FINAL_GROSS текущего CASE и существующий QC;
последний AFTER автоматически не копируется в финальный capture.

## Запуск

Используется тот же pinned tool venv и паспорт, что в
[инструкции OPC клиента](opc40200-gateway-runtime.md).

```powershell
.\.venv-scale-gateway\Scripts\python.exe tools/assembly_scale_opc_gateway.py --profile C:\ScaleConfig\assembly-post.json --runtime C:\ScaleData\assembly-post --lease-db C:\ScaleData\opc-device-leases.sqlite
```

`--once` выполняет один цикл. HTTPS dedicated sender задаётся прежними переменными
`STORE_SCALE_API_ORIGIN`, `STORE_SCALE_SENDER`, `STORE_SCALE_PASSWORD`; их названия
сохранены для совместимости gateway tools, при сборке учётная запись должна иметь
именно warehouse_scale_ingest и назначение текущего устройства/склада. Это не
учётная запись бизнес-оператора. Секреты не печатаются.

Store и assembly инструменты имеют **одинаковый абсолютный default lease DB**
`<repository>/runtime/opc-device-leases.sqlite`. При установке службы задают один
явный `--lease-db` для всех адаптеров физического поста. Outbox каждой станции
остаётся в её runtime каталоге. Разные gateway host пока не имеют распределённого
hardware claim, поэтому один физический пост нельзя независимо запускать на двух
host без серверного координатора.

## Подтверждение и восстановление

Gateway проверяет только неизменяемый `archive` ответа: исходные session/step/phase,
device/capture identity, policy/calibration/time, canonical source SHA, capture key
и массу последнего sample. `archive.stock_posted` обязан быть false. Текущий `step`
может быть ARMED/READY/APPLIED/DISCREPANCY; READY без posting не подменяется успехом
товарной операции. Инструмент сообщает `stock_outcome: READ_STEP`.

При HTTP503/timeout сохраняются исходные body/raw и preallocated capture_id.
Повтор разрешён даже после смены фазы server queue, поскольку отправляется прежний
архивный факт. Никаких новых capture ID или повторного физического измерения для
того же ожидающего payload нет. Payload conflict/постоянный API отказ приводит
к SUSPENDED и разбору. Старый пакет может быть повторён до нового OPC подключения;
перезапуск весов не мешает восстановить потерянный HTTP ACK.

Raw evidence здесь имеет **protocol_version1.1 / WAREHOUSE_ASSEMBLY**. Вместо
zero_observation присутствует `zero_reference` с настоящими session_id/step_id/
phase/tare_capture_key из серверной очереди. Отсутствующий tare reference не
угадывается. Zero не фабрикуется из current load или из предыдущего AFTER.
Текущий v1.0 store/warehouse evidence serializer не менялся.

Основной assembly API использует прежний header1.0; только raw1.1 запрос отправляет
`X-Scale-Protocol-Version: 1.1`. Raw ACK проверяет протокол, canonical evidence SHA,
capture identity/SHA, ARCHIVED и GATEWAY_REPORTED с binding PENDING/MATCHED.
Два архива пока отдельны; сам raw archive не является атомарным business guard
или независимой аттестацией физического оборудования.

## Проверка

- Строгие archive ACK: неверные scope/phase/hash/mass/time/policy и malformed ответы
  не принимаются; READY без stock effect допускается только как hardware archive.
- Потеря ответа после архивации: exact body повторяется, даже если очередь уже
  показывает AFTER. HTTP fixture проверяет реальные paths и отдельные headers1.0/1.1.
- Настоящий шифрованный локальный OPC server: BEFORE0.5, исходное плато, фактический
  переход к AFTER1.5, свежие samples и совпадение с AssemblyCapture/AssemblyScaleEvidence.
- Нет физических весов, аппаратного пилота, проверки реальной этикетки/тары или
  независимого утверждения stock effect. Это следующие сквозные приёмочные шаги.

## Сверка после заблокированной укладки (gateway)

Forward increment 15.10.2026: gateway поддерживает отдельный phase RECONCILE и immutable reconciliation_id из серверной очереди. Он читает текущую стабильную GROSS-серию без требования положительного прироста; исходная тара сессии не заменяется новым нулём. POST остаётся на прежнем capture endpoint/header1.0 с отдельным DTO; raw имеет отдельный kind WAREHOUSE_ASSEMBLY_RECON/protocol1.2 и zero_reference с reconciliation_id/phaseRECONCILE. Старые BEFORE/AFTER и raw1.1 canonical bytes не меняются.

ACK обязан содержать тот же reconciliation_id, COMPLETED либо DISCREPANCY, stock_posted:false и posting:null в envelope. Gateway не может объявить APPLIED или назначить нового business actor при сверке. Пара проходит тот же atomic local bundle/lease/outbox путь. Измерение разрешается только по фактической серверной AUTHORIZED очереди после отдельных operator HOLD и controller authorization; сам gateway этих команд не отправляет.

Проверки:46 focused Python/HTTP/journal tests PASS; дополнительный encrypted localhost OPC тест проверяет неизменную текущую массу (без delta-gate), отдельный DTO и canonical raw1.2. Native активация/реальное устройство этим локальным тестом не утверждаются. После native successful reconciliation старый шаг отображается CANCELLED нейтрально, не как товарное подтверждение.


## Live native TEST приёмка 15.10.2026

После активации native recovery выполнен encrypted localhost OPC→реальный HTTP→Oracle проход TEST1032: фактическая серия GROSS0.5, RECONCILE COMPLETED, исходный шаг CANCELLED, session OPEN; raw1.2 binding MATCHED. Принятый baseline, content version и физический источник остались неизменными, товарной операции и step-use нет. [Машиночитаемый отчёт](../../reports/retailcase/2026-10-15/assembly-scale/opc-reconciliation-http-report.json). Это не проверка физических весов. Fixture затем штатно выведен из работы; success HTTP replay после retirement не выполнялся. Exact native replay исходного raw отдельно проверен владельцем внутри caller rollback, без восстановления активного устройства.
