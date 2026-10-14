# NI06.3 — самостоятельная товарная паллета,103
2026-10-10-103-standalone-stock-pallet-tare APPLIED RABAEV/orcl,9 statements/0 errors; BOOK_CMD VALID. Использованы прежние BOOK/HU identity, существующая товарная RRL_PALLETS и single LOAD_SHIPMENT. Дополнительная внешняя пустая паллета не создаётся.

STOCK root допускается при одной актуальной положительной RRL_REMAINS CELL, текущем складе, физическом типе PALLET, отсутствии родителя/CASE carrier/already loaded. Stock closure входит в прежний Root план; current stock_version/cell повторно проверяются после блокировок. Товарное количество не является количеством тары: одна самостоятельная паллета — один hold. CANCEL непустой паллеты отказан.

[Одноразовый сценарий](../../scripts/ni063_fullpal_tare_case.py) PASS: фактическая STOCK/FULLPAL3, BOOK1/free0, штатное whole picking move и existing ST bind, whole same-warehouse relocation, single actual load; current dedicated driver ACCEPT/replay закрывает claim и даёт warehouse0/vehicle1. Goods event для tare accept0, дополнительного контейнера нет. Только собственные P/H fixture очищены прежним Root; immutable history остаётся.

Межскладское перемещение физически занятой тары не получает новый custody автоматически; требуется отдельный межскладской процесс. Полный NI06.3 ещё открыт: недостача/план потребности, repack, moving damaged lineage/independent acceptance.
