# NS21 — общий SOFT пул открытых заказов

09.10.2026, продолжение по поручению выполнять все спринты без прежнего ограничения18:00. NI03.2 остаётся in_progress.

Существующий RRL_STOCK_RESERVATION и единый RRL_STOCK_POSTING_API сохраняются. Старый произвольный SOFT по PICK_PLAN/WAVE не считается готовым распределением общего пула. Новая команда RESERVATION_ALLOCATE_POOL использует те же журнал операции/outbox/guards и replay; SOFT не привязан к паллете, ячейке или волне и не увеличивает H.

Требование: 02_store_orders.md, «Запас и мягкий резерв»; NS21 TC01–04/TT01. Правило долей — inventory/domain/pool_allocation.py: пропорциональные целые quantum, минимум одна каждому при достаточном бюджете, при меньшем бюджете более ранняя отправка. Остаток полного quantum распределяется по недополученной доле; исходная ERP потребность не переписывается. Вычисление ограничено числом строк, не числом единиц товара.

Планирование читает RRL_STOCK_POOL_READ. Snapshot включает source stock/version/eligible free, открытые строки заказа/конверсию/очерёдность и действующие pool reservations. Из marked stock учитываются только AVAILABLE физические единицы без чужого HARD; несколько профилей не умножают количество. Core принимает только trusted server hints, проверяет snapshot до и после sorted locks и границы/quantum. Изменившийся снимок — whole-command retry, без промежуточного commit. Один logical pool anchor на warehouse/SKU сериализует конкурирующие расчёты; источники входят в прежний stock closure. Independent warehouse/SKU pools не используют глобальную X блокировку.

Настройка существующей RRL_RECEIPT_SKU_RULE расширяется STOCK_ALLOC_CLASS/SHIP_FROM_STOCK/PICK_STEP_BASE/ALLOCATION_VERSION. DRY_RACK по умолчанию из наличия; FRESH/OTHER без явного флага — плановая потребность. Неизвестный legacy ассортимент не объявляется сухим автоматически. Кратность отбора отдельно от кратности пополнения. POOL_WARE_ID в reservation — логическое место потребности; старые физические WARE_ID/CELL/UID остаются NULL.

019 APPLIED: schema/read/command/context/root VALID. Checkpoints251/252 сохраняют прежние root/context; installation snapshots004/005 неизменны при последующей эволюции. API preview/allocate и SKU policy подключены; панель общего пула находится в существующем customer-orders.html. Первый warehouse/SKU rule создаётся прежней настройкой приёмки с реальной ячейкой отбора; отдельная настройка обеспечения меняет только allocation fields, версия защищает от потерянного обновления. Исправлен прежний недопустимый bind :mode в receiving configuration.

Адресный dev-case QPOOLf518da3cde / orders1734–1736 / lines3220–3222 прошёл:100→40/30/30, идентичный replay, новый расчёт сохраняет3 SOFT без физической привязки, отмена→70, FRESH inherited→0. P100/H0 до cleanup; собственный запас восстановлен root INVENTORY_COUNT, история сохранена. Четыре domain cases passed. Независимая и браузерная приёмка не объявлены. Перевод SOFT→HARD и старые SOFT commitments ещё открыты.

Границы: до2000 open lines/reservations и500 source lots за один pool. Превышение даёт явный отказ, а не скрытый частичный результат. Промышленная мощность и внешняя SAP/Track & Trace квитанция этим ticket не доказываются. Qwen проверяет независимо после поставки; широкие прогоны не запускаются автоматически.

020 APPLIED: существующий WAVE_LAUNCH потребляет allocation общего пула и создаёт HARD в прежнем root commit. Bridge читает CUSTOMER_ORDER_ROW_ID из существующего PICK_PLAN_LINE; несколько projection sources группируются по строке, проверяется общая доля, version и pool anchor. Превышение/нет обязательной доли — отказ до проводки. Из следующей SOFT потребности вычитаются текущий HARD и подтверждённый FACT_QTY, чтобы уже обеспеченный или отобранный товар не обещался повторно.

Реальный адресный case QPOOLd03d25fda8 / WAVE225 прошёл: pool70 после отмены, launch40 → P100/H40, SOFT этой строки0/CONSUMED, повтор launch не увеличил H, следующий pool30 для другого заказа. Два concurrent calculations также прошли. Собственная волна отменена прежним root WAVE_CANCEL, own stock обнулён через INVENTORY_COUNT; история сохранена. Обнаруженный при первом запуске повтор обещания уже HARD-обеспеченной потребности исправлен в snapshot. Не считать исходный провал пройденной проверкой.

Slow SQL decision: bounded preview99.71ms (предыдущий12.85ms), pool≤2000lines/500lots, wave≤200lines. Пока использовать существующие ключи SKU/stock/planline; расширение индекса только по реальному плану при устойчивом превышении500ms. Промышленный объём этим случаем не подтверждён.

Старый active SOFT без POOL_WARE_ID вызывает явный POOL_LEGACY_SOFT_REQUIRES_RECONCILIATION при stock-backed pool. Автоматическое суммирование старых разных документов не выполняется; освободить/пересчитать через прежние root команды. Generic WAVE consumer binding, mini/MAX и duty lifecycle остаются открыты.
