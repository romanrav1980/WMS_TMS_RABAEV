# NS00: тестовый набор в RABAEV

7 октября 2026 года. Fixture data only; миграции и DDL не применялись. Владелец разрешил разработку в выделенном ORCL/orcl, непосредственно в RABAEV. Изменяются только owned тестовые строки. [[nicora_ns00_dev_baseline]] описывает прежнюю перекомпиляцию, [[nicora_ns00_environment]] — запуск и evidence.

## Привязка ядра DS-BASE

| Таблица | Явные ключи | Строк |
|---|---|---:|
| RRL_WARES | ID=9807 | 1 |
| RRL_CELLS | CELL=DS-BASE-P1 / DS-BASE-RES1 / DS-BASE-EXP-IN | 3 |
| RRL_ARTICULS | ACTICUL=DS-BASE-D10 / D02 / D04 / FRESH / UNIT-SKU | 5 |
| RRL_CUSTOMER | CUSTOMER_ID=-980701 / -980702 | 2 |
| RRL_PRIHOD_NAKLAD | ID=-980700 | 1 |
| RRL_PALLETS | UID_PALLET=DS-BASE-B1 / DS-BASE-B2 | 2 |
| RRL_REMAINS | UID_POLETA=B1/B2 с префиксом DS-BASE-, CELL=P1/RES1 с тем же префиксом | 2 |
| RRL_CUSTOMER_ORDER | CUSTOMER_ORDER_ID=-980711 / -980712 / -980713 | 3 |
| RRL_CUSTOMER_ORDER_ROW | CUSTOMER_ORDER_ROW_ID=-980711 / -980712 / -980713 | 3 |

Всего 22 строки. Две партии по 50 коробок D10; COUNT_SHT_IN_KOR=24, физический REMAIN=1200 штук на каждой паллете, всего 2400. Заказы 40/30/30 коробок имеют PACK_COUNT=40/30/30 и ORDER_QTY=960/720/720 PCS. Участки склада заблокированы для обычных операций, клиенты неактивны, документы DRAFT. Отрицательные ID и выбранные строки сначала проверены на отсутствие collision; без внешнего provenance файл существующие ключи не принимаются за собственные.

Логические партии B1/B2 представлены двумя UID и их сроками; это минимальная legacy привязка стенда, не общий регуляторный batch contract. Декларативные машины, ставки, смешанный HU1, режимы магазина, мягкие резервы и Track & Trace не объявлены реализованными. NS02–NS04 проверят их отображение и GAP. Начальные остатки вводятся как fixture, не как бизнес-приёмка без документов SAP.

## Контракт записи и очистки

[План](../../tools/nicora_environment/fixture_plan.py) содержит allowlist таблиц/ключей. [Seed](../../db/fixtures/nicora_ns00/seed.sql) и [reset](../../db/fixtures/nicora_ns00/reset.sql) — bind-шаблоны без commit; исполняются только [CLI](../../tools/nicora_environment/__main__.py) после проверок provenance, target, DML triggers и внешних ссылок. Дополнительные nullable поля SKU выбираются из reviewed планов; отсутствующее измерение не выдумывается.

Одна транзакция — lock таблиц NOWAIT, проверка owned и внешних ссылок, hash внешних данных, удаление ровно известных ключей в обратном порядке, вставка в прямом порядке, повторный hash, commit. Legacy таблицы не имеют достаточных PK/unique constraints, поэтому короткий административный table lock исключает concurrent insert в эти же таблицы. Loader не выполняется как складской runtime или нагрузочный job. Любые внешние связи с набором запрещают reset. Подтверждённое изменение тестового SKU по API может быть внесено в manifest только после сравнения всех остальных полей; этот helper допускает два поля NS00, не произвольную правку.

[Manifest](../../runtime/test-evidence/nicora_ns00/fixture-manifest.json) хранит exact live rows, hashes, target и план. Потерянный manifest не восстанавливается путём присвоения существующих строк. Pre-commit .pending.json сохраняется до commit; следующий вызов автоматически подтверждает только совпавший committed snapshot, несовпадение требует разбора и не вызывает очистку.

## Проверено в живом Oracle

Seed/repeat/reset/cleanup/reseed прошли; repeat=UNCHANGED 22 строки, cleanup=0, reseed=22. Защиты без manifest и при изменённых owned строках отказали без изменений. Искусственный ORA-01400 после удаления набора и первой вставки откатил всю транзакцию; fingerprint до/после совпал. Внешние данные совпали по всем сохранённым стадиям: 3864 строки RRL_REMAINS, связанные паллеты и полные остальные таблицы вне allowlist. Все 758382 исторические паллеты целиком не экспортировались: DML ограничен двумя UID, активные trigger отсутствуют, preservation проверяет связанные с остатком паллеты. Это ограничение явно отражено в evidence, не полный backup.

[Cross-stage report](../../runtime/test-evidence/nicora_ns00/cross-stage-preservation.json), [отказы/rollback](../../runtime/test-evidence/nicora_ns00/negative-probes.json), [live balance](../../runtime/test-evidence/nicora_ns00/verify.json). INVALID=0, активные ошибки компиляции=0; все шесть Oracle verification профилей PASS. Кириллические значения этим ASCII fixture не записывались.
