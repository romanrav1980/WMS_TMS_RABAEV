# NI06.3 — потребность тары существующей волны,104
Read-only inventory port/infrastructure/API and existing tare-assembly screen; Oracle DDL нет. GET /api/inventory/tare/warehouses/{ware}/waves/{wave}/forecast requires tare_view + current warehouse binding; wave must belong to that warehouse.

Для текущих unshipped/uncancelled самостоятельных CASE группируются existing PALLET_TYPE_ID и незакреплённые места. Недостача=max(unbooked-free,0); прежние holds уже исключены из свободного количества, поэтому второй раз не вычитаются. Если физический пересчёт отсутствует, доступность/недостача null и OBSERVATION_REQUIRED.

Вложенные CASE не считаются самостоятельной тарой; их количество показано как scope warning. FULLPAL требует явного физического типа BOOK103. Незавершённые GOOD vehicle→warehouse offers показываются как proposed_return_quantity отдельно, без обещанной даты и без увеличения free. Запрос не резервирует тару и не доказывает обеспеченность всей смены.

[Сценарий](../../scripts/ni063_forecast_case.py) PASS read-only real Oracle/API: существующая wave369 имеет unbooked2/free1/shortage1. Max10000 CASE в волне,100 типов; большее окно требует разделения. SQL cxtnfuakmyw6v73.319ms/2, retain bounded/indexed wave and current-balance PK; NI06.3 owner checks plan/projection if history grows.
