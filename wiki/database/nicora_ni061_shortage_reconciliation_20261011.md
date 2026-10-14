# Сверка недостающего межскладского товара
294: существующая частичная291/292 приёмка остаётся единственной проводкой. GET /api/inventory/interwarehouse/receipts/{receipt}/shortage читает один READ ONLY snapshot: текущий RUSERS/right/склад одного плеча, APPLIED receipt, frozen original+accepted units, original load custody и текущие единицы/число зарегистрированных кодов.

Для обычного товара показывает исходное3/принятое1/недостачу2. Для маркированного дополнительно вычисляет точное исходное подмножество original_source_units minus source_units; количество сверяется точным Decimal с receipt.Expected-Actual. Отображает printed unitID, количество/UOM, текущие UID/cell/status/version и count кодов без раскрытия QR. Изменившееся текущие состояние выделяется как требующее расследования, а не как доказательство потери. Максимум10000 исходных/полученных единиц. Никаких записей запаса/марок/ответственности/GovACK.

Raw interwarehouse UI выбирает ранее принятую поставку и показывает сверку. Актуальные actor/API и serial защищают от позднего ответа; read не создаёт durable write intent.

Фактические291 и292:3/1/2, ordinary0units; marked2 неполученные ISSUED/по2кода, custody остаётся открытой, protected20-20. Browser/independent не проведены. Реальный акт утраты/позднее получение/разрешение ответственности ещё не реализованы.

SQL: первый cold JSON_TABLE 19.589ms/815buffers на2 executions, следующие две чтения добавили36buffers и~2.55ms в среднем. Bounded missing JSON + physical-key unique lookup; явно выбран nested loop и существующий RRL_RECEIPT_UNIT_PHYSICAL_UK, code count по RRL_WMS_REC_CODE_PAL_IX. Новый индекс/cache не нужен.
