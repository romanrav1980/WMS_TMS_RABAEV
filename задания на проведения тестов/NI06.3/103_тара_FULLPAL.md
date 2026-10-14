# Qwen — NI06.3,103
Новый собственный STOCK/FULLPAL fixture: один положительный current cell, PALLET type, BOOK1, existing picking move/ST binding, standalone load, independent driver ACCEPT. Тара warehouse-1/vehicle+1, goods только исходная погрузка, original claim TRANSFERRED/replay.
Отказы: TROLLEY type для STOCK, split UID по двум положительным ячейкам, CASE carrier child, upper parent, foreign warehouse, empty-source/already-loaded, CANCEL nonempty. Никакого fake PP/снятия HARD/изменения товары от BOOK.
После actual case longest SQL bounded analysis; не запускать одноразовый author-case повторно.
