# Стратегический план WMS+MES+Traceability

Статус: принят как рамка реализации после EDD.

Дата: 2026-05-17.

Связанный документ: [Engineering Design Document](../architecture/wms_mes_traceability_edd.md).

## Цель

Построить из текущего проекта WMS/TMS полноценную систему WMS+MES для фабрики кормов, где:

- склад сырья, производство, склад готовой продукции и отгрузка работают как единый операционный контур;
- `Меркурий` и `Честный Знак` не смешиваются в одной модели;
- вся прослеживаемость строится через отдельный `Traceability Service`;
- производственная линия не зависит напрямую от доступности внешних государственных API;
- каждый факт, API-вызов, внешняя отправка и повтор фиксируются в audit/outbox;
- для партии, ВСД, DataMatrix или SSCC можно построить genealogy до клиента.

## Стратегические решения

1. Основной backend стек текущего этапа: Python/FastAPI.
2. Текущий Oracle `RABAEV` остается system of record на переходный период.
3. Новые write-операции идут через API и PL/SQL API packages, а не прямыми SQL-записями из клиентов.
4. Для гарантированной доставки используется transactional outbox:
   - сначала Oracle-backed outbox;
   - затем RabbitMQ или Kafka, когда появится реальная необходимость в broker layer.
5. PostgreSQL не внедряется на текущем этапе. Текущая реализация является Oracle-first; PostgreSQL возможен только как future extension после отдельного решения.
6. `Меркурий` реализуется как отдельный connector/adaptor.
7. `Честный Знак` / CRPT реализуется как отдельный connector/adaptor.
8. `Traceability Service` хранит внутренние связи между сырьем, ВСД, production order, finished goods lot, DataMatrix, SSCC, shipment и customer.
9. Legacy C# и `Tserver` сохраняются до тех пор, пока конкретные сценарии не перенесены и не проверены.
10. Админка должна иметь отдельные права на:
   - API audit;
   - external outbox;
   - права пользователей;
   - регуляторные операции;
   - replay/retry.
11. Любая Oracle-миграция идет только через versioned scripts и wiki mirror. Удаление таблиц без отдельного явного подтверждения запрещено.

## Целевая Карта Сервисов

```text
Admin UI / Terminal Web-PWA / Legacy Desktop
                |
                v
          WMS API Gateway
                |
   +------------+-------------+
   |            |             |
  WMS          MES      Traceability Service
   |            |             |
   +------------+-------------+
                |
          Oracle RABAEV MVP
                |
        Transactional Outbox
                |
   +------------+-------------+
   |                          |
Mercury Connector       Chestny Znak Connector
   |                          |
VetIS / Mercury         CRPT / Honest Sign
```

## Этапы Развития

### Этап 0. Зафиксировать текущую устойчивую базу

Цель: не потерять уже восстановленную и скомпилированную базу.

Результат:

- wiki mirror актуален;
- все примененные migrations описаны;
- API audit/replay работает;
- права админки работают через legacy `RUSERS` / `USER_GROUP` / `RIGHTS`;
- anti-mojibake check выполняется перед завершением изменений.

Статус: в основном выполнено.

### Этап 1. Traceability Spine

Цель: создать внутренний позвоночник прослеживаемости.

Нужно добавить:

- `RRL_TRACE_EVENT`;
- `RRL_TRACE_EDGE`;
- `RRL_EVENT_OUTBOX`;
- `RRL_ADAPTER_REQUEST_LOG`;
- минимальный QA hold;
- read API для genealogy.

Результат:

- можно строить цепочку сырье -> производство -> готовая партия -> DataMatrix/SSCC -> отгрузка;
- outbox гарантирует, что событие не потеряется;
- внешние адаптеры можно подключать без изменения операторских экранов.

### Этап 2. MES Core

Цель: сделать производственный контур не набором разрозненных записей, а управляемым процессом.

Нужно добавить:

- production order;
- рецептуры;
- план/факт сырья;
- смена/линия;
- выпуск finished goods lot;
- JSON-файловый обмен выпуска.

Результат:

- производственная партия создается управляемо;
- сырье связано с производством;
- выпуск можно принять из внешней системы через папку + JSON;
- ошибки импорта не создают частичные данные.

### Этап 3. Labeling, Printing, Aggregation

Цель: закрыть Честный Знак на уровне внутренней готовности.

Нужно добавить:

- заказ/импорт кодов;
- безопасное хранение DataMatrix;
- print jobs;
- scan verification;
- агрегация коробов и паллет;
- SSCC;
- режим клиента: `ITEM_CODES`, `SSCC`, `MIXED`.

Результат:

- для каждого DataMatrix известны партия, production order, паллета, SSCC, отгрузка и клиент;
- для клиента, принимающего агрегацию, можно передавать SSCC;
- для клиента без агрегации можно передавать полный список CIS.

### Этап 4. Regulatory Connectors

Цель: подключить реальные внешние системы через audit/outbox, не останавливая производство.

Нужно сделать:

- mock Mercury connector;
- mock CRPT connector;
- adapter request log;
- retry policy;
- dead-letter handling;
- admin page для внешних отправок;
- потом реальные сертификаты, подписи и внешние API.

Результат:

- можно видеть каждую внешнюю отправку;
- можно повторить неуспешную отправку;
- можно доказать, какой payload был отправлен и какой ответ получен;
- линия не блокируется из-за временной недоступности внешнего API.

### Этап 5. Shipment и Recall

Цель: довести цепочку до клиента и обратного поиска.

Нужно добавить:

- shipment readiness check;
- shipment lines / pallet links;
- контроль legal readiness;
- УПД / customer package;
- recall cases;
- поиск по raw lot, VSD, finished lot, DataMatrix, SSCC.

Результат:

- система не разрешает отгрузку при критичном regulatory/quality gap;
- можно быстро определить, куда ушло сырье или партия;
- можно найти клиента по конкретному коду маркировки.

### Этап 6. Optional Broker / PostgreSQL Evolution

Цель: после стабилизации Oracle-first API/outbox отдельно решить, нужен ли внешний broker или выделение новых контуров из Oracle.

Условие перехода:

- outbox и API уже доказали модель;
- есть несколько независимых consumers;
- есть реальная потребность в replay или stream processing;
- нагрузка на scan/labeling/shipment требует отдельного масштабирования.

Возможный результат:

- новые bounded contexts могут жить в PostgreSQL;
- Redis отвечает за locks/cache/idempotency;
- RabbitMQ или Kafka принимает durable event delivery;
- Oracle остается совместимой с legacy до полного вывода старых потоков.

Это не часть текущего Sprint 1 и не текущая принятая база данных.

## Приоритеты Реализации

1. Сначала safety и versioning.
2. Затем traceability spine и event outbox.
3. Затем worker и mock adapters.
4. Затем MES production order и file exchange.
5. Затем labeling/aggregation.
6. Затем shipment/recall.
7. Затем реальные Mercury/CRPT adapters.
8. Затем перенос legacy сценариев и, только при отдельном решении, broker/PostgreSQL evolution.

## Критерии Готовности Архитектуры MVP

MVP считается архитектурно состоятельным, когда:

- production batch создается через API;
- raw material usage связывает сырье с выпуском;
- traceability edge строит genealogy;
- DataMatrix и SSCC связаны с партией и паллетой;
- каждое внешнее событие лежит в outbox;
- mock adapters могут выполнить retry;
- API audit и external audit доступны в админке;
- проверки кодировки, verify SQL и smoke tests повторяемы;
- live Oracle не содержит invalid objects после миграции.

## Риски

- Скрытая бизнес-логика в WinForms и `Tserver`.
- Прямые записи legacy-клиентов в Oracle в обход нового API.
- Ошибки идемпотентности при повторе файлов/вызовов.
- Расхождение фактического состава паллеты и электронной агрегации.
- Недоступность Меркурия или Честного Знака в момент production/shipment.
- Потеря полного DataMatrix в открытых логах.
- Разрастание временных mock-интеграций в production без адаптерного слоя.

## Архитектурные Запреты

- Не смешивать ВСД и DataMatrix в одной таблице как одну сущность.
- Не вызывать внешние государственные API прямо с производственной линии.
- Не давать новым терминалам Oracle credentials.
- Не удалять legacy-таблицы как часть MVP.
- Не логировать секреты, приватные ключи и полные чувствительные payload без маскирования.
- Не делать replay без idempotency key и audit trail.

## Стратегический Следующий Шаг

Первый практический шаг реализации: `migration 008` для traceability spine и outbox, затем worker и admin page внешних отправок.
