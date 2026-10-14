# NI05.3: выгрузка обычной WMS-паллеты

Миграция 2026-10-14-1316-stock-pallet-unload, PREPARED. На собственном рейсе33571 приёмка отказала UNLOAD_PALLET_SOURCE_REQUIRED: старый RRL_STORE_UNLOAD_CORE принимал метод PALLET только для CONTAINER/PALLET, хотя обычный ROOT_STOCK_TYPE уже подтверждён при физической погрузке.

Используем существующий неизменяемый RRL_TT_LOAD_FLOOR_FACT именно исходной погрузки: ROOT_STOCK_TYPE, тот же root, согласованный pallet_type_id, DEPARTED/APPLIED. Текущие настройки SKU/адресата не заменяют отгрузочный факт. Отсутствие доказательства отклоняется. Приёмка остаётся в прежнем ядре, остатки повторно не списываются. HU и ручная выгрузка сохраняют свои правила; способ ROLL_CAGE этим изменением не расширен.

Свежий LIVE checkpoint содержит package body и INVALID=[]; rollback только кода, журнал не удаляется. Actual/UI/SQL evidence после применения.

## Installed1326
Миграция применена в RABAEV/orcl, USER_ERRORS=[], INVALID=[]. [B03 результат](../components/retailcase_b03_driver_delivery_20261014.md), report46. Runtime mirror обновлён. Ранее указанный PREPARED — история подготовки, текущий статус INSTALLED / AUTHOR_DEV_CASE.
