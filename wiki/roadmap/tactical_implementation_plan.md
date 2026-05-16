# Тактический План Реализации

## Назначение

Этот документ фиксирует ближайший порядок работ по задаче WMS/MES для фабрики кормов: выпуск партий готовой продукции, вовлечение сырья, Меркурий, Честный знак, агрегация, JSON-файловый обмен, API-граница и будущие Android-терминалы.

Стратегическая рамка описана в [`strategic_development_plan.md`](strategic_development_plan.md). Этот план отвечает на вопрос, что делать дальше практически.

## Уже Сделано

В Oracle `RABAEV@127.0.0.1:1521/orcl` уже применено:

- `2026-05-17-001-feed-factory-traceability`: базовые таблицы и колонки.
- `2026-05-17-002-feed-factory-traceability-api`: PL/SQL пакет `RRL_PRODUCTION_API`.
- `RRL_PRODUCTION_API` package и package body имеют статус `VALID`.
- Итоговая проверка live-схемы: `458 VALID`, `0 INVALID`.
- Текущая кодовая точка: `444354a`.

Ключевые файлы:

- [`../../db/migrations/2026-05-17_feed_factory_traceability/001_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/001_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/002_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/002_apply.sql)
- [`../database/feed_factory_traceability_schema.md`](../database/feed_factory_traceability_schema.md)
- [`../requirements/feed_factory_mercury_crpt_tz.md`](../requirements/feed_factory_mercury_crpt_tz.md)

## Правила Безопасности

- Не удалять таблицы без отдельного явного подтверждения.
- Каждое изменение Oracle оформлять версионной миграцией: `apply`, `rollback`, `verify`, описание в wiki.
- Перед применением Oracle-миграции делать кодовую фиксацию.
- Новый прикладной код не должен напрямую писать в traceability-таблицы, если операция уже есть в `RRL_PRODUCTION_API`.
- Файловый обмен и внешние интеграции должны быть идемпотентными по `messageId`, operation ID или idempotency key.
- Smoke-тесты должны работать либо в disposable-среде, либо чистить только свои фиксированные тестовые ключи.

## Поток 1: Укрепление Oracle-Контракта

Цель: сделать слой базы достаточно устойчивым для API и файлового воркера.

Работы:

1. Проверить качество legacy-данных перед добавлением внешних ключей.
2. Добавить безопасные check constraints для статусов.
3. Добавить view для чтения API:
   - сводка партии производства;
   - сводка паллет партии;
   - сводка CRPT/SSCC-агрегации;
   - статус Меркурия;
   - статус обработки файлового обмена.
4. Расширить `RRL_PRODUCTION_API` read-методами или cursor-процедурами, если API нужен стабильный read-контракт.
5. Спроектировать command journal, если синхронных вызовов будет недостаточно для контроля конфликтов.
6. Готовить миграцию `003_*` только после ревью состава изменений.

Критерий готовности:

- API может выполнять все нужные записи по производству через `RRL_PRODUCTION_API`.
- Read endpoints не требуют хрупких ad hoc join в C#-коде.
- Verify показывает `0 INVALID` текущих объектов.

## Поток 2: MVP API-Сервера

Цель: создать стабильную сервисную границу для всех новых операций изменения данных.

Рекомендуемый стек:

- ASP.NET Core на текущем .NET LTS.
- Oracle.ManagedDataAccess.
- OpenAPI/Swagger.
- Структурные логи с request ID и operation ID.
- Конфигурация через environment variables или защищенный конфиг, без hardcoded DB strings.

Первые endpoints:

- `GET /health`
- `GET /db/ping`
- `POST /api/production-batches`
- `POST /api/production-batches/{id}/pallets`
- `POST /api/production-batches/{id}/raw-usage`
- `POST /api/production-batches/{id}/crpt-codes`
- `POST /api/production-batches/{id}/aggregations`
- `POST /api/production-batches/{id}/mercury`
- `GET /api/production-batches/{id}/status`

Критерий готовности:

- API вызывает `RRL_PRODUCTION_API`.
- Каждая mutation требует idempotency key.
- Есть OpenAPI contract.
- Integration tests запускаются против локальной Oracle VM.

## Поток 3: JSON-Файловый Обмен

Цель: принимать выпуск партий из внешней системы через папку и JSON.

Работы:

1. Создать worker/service для папок:
   - `exchange/production_release/in`
   - `processing`
   - `archive`
   - `error`
   - `out`
2. Принимать только атомарную передачу `.tmp` -> `.json`.
3. Валидировать JSON schema и обязательные поля.
4. Регистрировать файл в `RRL_FILE_EXCHANGE_LOG`.
5. Создавать партию через API или напрямую через `RRL_PRODUCTION_API`, если worker работает внутри доверенного backend-контура.
6. Писать response JSON в `out`.
7. Успешный входной файл переносить в `archive`.
8. Ошибочный входной файл переносить в `error` с диагностическим ответом.

Критерий готовности:

- Повторный `messageId` обрабатывается идемпотентно.
- Невалидный JSON не создает частичных бизнес-данных.
- Success/error responses воспроизводимы и понятны внешней системе.

## Поток 4: Адаптеры Меркурия И Честного Знака

Цель: изолировать регуляторные интеграции от операторских приложений.

Честный знак:

- маппинг `RRL_CRPT_CODES` и `RRL_CRPT_AGGREGATION` в исходящие документы;
- поддержка отгрузки по `SSCC` для клиентов, принимающих агрегацию;
- поддержка отгрузки полным списком `CIS` для клиентов, которые агрегацию не принимают;
- хранение внешних document ID и статусов;
- повторы через outbox.

Меркурий:

- маппинг партии производства и вовлеченного сырья на понятия VetIS/Mercury;
- хранение eVSD и stock entry identifiers;
- обработка асинхронных статусов;
- изоляция XML/WSDL и adapter-specific сложности от desktop и terminal clients.

Критерий готовности:

- Оба адаптера могут работать в mock-режиме до получения реальных учетных данных.
- Каждый исходящий запрос имеет сохраненный статус и внешний ID после получения ответа.

## Поток 5: Переход Legacy-Клиентов

Цель: сохранить работоспособность WinForms и `Tserver`, но постепенно переносить write-операции за API.

Работы:

1. Не ломать существующие прямые Oracle-потоки.
2. Найти write-операции, пересекающиеся с производственной traceability.
3. Подключать desktop client к API только после готовности endpoint.
4. Для терминального контура провести pilot на одной низкорисковой операции.
5. До приемки pilot сохранять путь отката к старому flow.

Критерий готовности:

- Нет регресса совместимости C# desktop client.
- `Tserver` сохраняет текущие операционные сценарии.
- Новые записи по производственной traceability проходят через новую границу.

## Поток 6: Android Terminal MVP

Цель: подготовить современный терминальный контур, не останавливая текущую работу склада.

Первые сценарии:

- login;
- scan pallet;
- показать production batch / SSCC / CRPT status;
- подтвердить приемку паллеты готовой продукции;
- понятно показать бизнес-ошибку API.

Критерий готовности:

- Android prototype использует только API.
- На устройстве нет Oracle credentials.
- Scanner flow работает с representative barcode/DataMatrix input.

## Первые Две Недели

1. Создать проект API server.
2. Добавить `GET /health` и `GET /db/ping`.
3. Добавить Oracle config и безопасное хранение secrets.
4. Реализовать `POST /api/production-batches` поверх `RRL_PRODUCTION_API.CREATE_PROD_BATCH`.
5. Реализовать endpoint привязки паллеты/SSCC.
6. Реализовать endpoint вовлечения сырья.
7. Добавить API integration smoke test против локальной Oracle.
8. Создать JSON schema для production release file.
9. Реализовать happy path файлового worker.
10. Готовить миграцию `003` только если API выявит недостающий DB contract.

## Следующий Месяц

1. Завершить feed-factory API MVP.
2. Завершить JSON-файловый обмен с `archive/error/out`.
3. Добавить endpoint CRPT aggregation и status read endpoint.
4. Добавить endpoint Mercury metadata и status read endpoint.
5. Добавить политику command/outbox processing.
6. Подготовить mock adapters для Меркурия и Честного знака.
7. Начать Android terminal prototype для read/status и одного confirmation flow.

## Definition Of Done

Задача не считается выполненной только потому, что таблицы существуют. Первый production-ready milestone достигнут, когда:

- внешняя система может отправить production release JSON;
- API/worker создает партию через `RRL_PRODUCTION_API`;
- паллеты, SSCC, CRPT codes, вовлечение сырья и Mercury metadata сохраняются;
- статус виден через API endpoint;
- outbox events готовы для adapter processing;
- smoke tests и rollback/cleanup procedures документированы и повторяемы.
