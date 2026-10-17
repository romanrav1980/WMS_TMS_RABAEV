# OPC40200: исполняемый клиент шлюза

В integrations добавлен read-only OPC UA клиент на pinned asyncua2.1.0, отдельный
физический device lease и real Read window для текущего магазинного capture.
Запуск/паспорт/ограничения: [runtime инструкция](../../docs/integrations/opc40200-gateway-runtime.md).
Архитектура: [[retailcase_weighing_gateway]].

## Реализовано

- Явный profile: endpoint, namespace URI v2, current WeightType,7 настоящих узлов,
  KG unit, no-tare mode, station/device, application URI и сертификаты.
- Basic256Sha256/SignAndEncrypt, server pin/URI/validity/usage проверки, без insecure
  OPC fallback и auto-trust. Опциональная UserName identity из окружения поверх OPC SecureChannel.
- Настоящие MaxAge0 Read/Both timestamps, strict Good/null/time/unit/tare/range gates.
  Старый source timestamp постоянного веса не обновляется выдуманным временем.
- Реальный zero, fresh stable positive sample window, existing store DTO; native
  RRL_SCALE_PACKET_READ сохраняет единоличную проверку разброса/дискретности.
- Отдельная fenced hardware lease на shared SQLite одного host; отдельный raw
  outbox128KiB и canonical ACK binding без второго stock writer.
- CLI [store_scale_opc_gateway.py](../../tools/store_scale_opc_gateway.py).

## Evidence

[Encrypted OPC server tests](../../tests/retailcase/test_scale_opc_client.py) создают
реальный TCP OPC server и сертификаты: positive zero/capture и совпадение с текущими
ScalePacket/ScaleEvidence, Bad/Uncertain/stale/unit/overload/tare, wrong pin и
reconnect requiring fresh zero. [Lease](../../tests/retailcase/test_scale_device_lease.py)
проверяет двух worker и fencing; [raw delivery](../../tests/retailcase/test_scale_evidence_delivery.py)
проверяет incorrect ACK/hash/identity и отдельный размер outbox.

Обычный API public импорт проверен на base Python без установленной asyncua.
Optional OPC dependency установлена только в изолированном tool venv, API requirements
не менялись. Полный gateway тест запускается именно gateway Python, обычный suite
без optional dependency явно пропускает OPC test module.

## Что не объявляется выполненным

Нет выбранной физической модели, полевого подключения/поверки/нагрузочного пилота,
распределённого hardware claim между host, CRL/CA rollout, warehouse OPC payload
projection и INCREMENTAL_ASSEMBLY domain effect. Текущий магазинный service требует
реальный zero до загрузки, новый zero после reconnect и свежие server timestamps
всех7 узлов; устройства с иным timestamp поведением требуют проверенного профиля.

Raw envelope — gateway-reported provenance, не независимая аппаратная аттестация;
отдельные capture/raw archives пока не являются атомарным business guard.
Нельзя расширить старый strict DTO OPC полями или подменить GROSS скрытым NET.

## AK06-D: assembly adapter

Добавлены реальный queue/capture transport для Assembly API и отдельная проекция
BEFORE/AFTER: [инструкция](../../docs/integrations/assembly-opc40200-runtime.md),
[CLI](../../tools/assembly_scale_opc_gateway.py). Оба инструмента используют один
default physical lease DB; context/outbox разделены по станции. AFTER ждёт
действительного изменения и свежего плато, BUTTON разрешает только backend queue.

Raw1.1 с zero_reference сохраняет связь с исходным EMPTY_TARE; новый zero не
производится и прежний v1.0 canonical hash не меняется. Archive ACK не требует
APPLIED и не объявляет stock effect. Native/API activation и бизнес-приёмка —
отдельная работа inventory owner, local OPC/HTTP test не подменяет её.

## Локальный журнал пары capture/raw — 15.10.2026

Оба OPC launcher сохраняют неизменную пару в bundles.sqlite одной FULL SQLite транзакцией под lease устройства. До нового чтения проверяется прежняя пара, после рестарта обе очереди восстанавливаются точными байтами до OPC connect. Раздельные ACK сохраняются. Legacy raw без исходного capture блокирует запуск с SCALE_LEGACY_RAW_NEEDS_RECONCILIATION; новый замер не подменяет потерянное тело.

[Runtime/recovery](../../docs/integrations/opc40200-gateway-runtime.md#atomic-local-captureevidence-staging--15102026), [12 fault tests](../../tests/retailcase/test_scale_bundle_journal.py). Это атомарное локальное сохранение, не общая HTTP/Oracle транзакция. Несколько процессов станции должны использовать один runtime и lease DB; multi-host claim не реализован.
