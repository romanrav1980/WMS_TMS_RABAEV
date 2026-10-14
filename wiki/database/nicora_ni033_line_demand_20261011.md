# NI03.3: точечная потребность оригинальной строки

Ticket171, в реализации. Выделяется существующий расчёт RRL_STOCK_POOL_READ в line_snapshot_json по исходному CUSTOMER_ORDER_ROW_ID. Общий пул вызывает ту же функцию, прежняя форма orders/порядок сохраняются. Новый планировщик/аллокация не вводятся.

Формула прежняя: requestedBASE − HARD − max(0,picked−pickedHardOverlap), нижняя граница0. UNIT_CODE/current exact UOM обязательны, отсутствие единицы не угадывается. Quantity означает незакреплённую потребность в BASE; это не доказательство отгрузки/неполучения товара. Прямое чтение одной строки не сканирует500 stock locations/2000 чужихorders.

Нужно для смешанного завершения волны: сохранить точный остаток источника после возврата части и фактической отгрузки другой части, не складывая разные единицы и не создавая второй движок восстановленной потребности. Миграция2026-10-11-171-existing-line-demand/saved live pool/paired rollback/no stock writes; применение пока не подтверждено.

APPLIED/VALID+dependent pool commandVALID/USER_ERRORS empty. Авторский first snapshot equality:2 warehouses/8 rows preserved exactly; after legitimate172 new orders/rule changes, scenario revised to compare saved old pure-read function against current function in SAME READ ONLY transaction/currentdata (no historical reset),2+8 rows PASS. Targeted helper fields equal current pool, warehouse/unit/open are explicit. Full pool2000 N+1 remains existing bounded backlog; targeted helper does not scan stock/globalpool. SQL helper1.704ms/10 (other2exec3.477ms), retain PK/line aggregation/bounds, owner inventory for set-based fullpool before larger production windows. No quantity/plan/order writes. Qwen tasks171 written; model notrun.
