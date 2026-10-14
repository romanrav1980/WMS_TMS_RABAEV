# NI05.3: текущий водитель и существующий журнал времени

Миграция2026-10-14-1302-driver-workspace PREPARED. Владелец transport; существующий RRL_TT_OPERATION_PLAN_API/RRL_TT_OPERATIONS, без второго транспортного или товарного реестра. Driver workspace использует существующую RRL_TRANSPORT_DRIVER_USER и активного RUSERS. ID не является аутентификацией.

Добавлены assert_driver и mark_driver_fact START/DONE: короткая транзакция, блокировкиNOWAIT в порядке binding→trip→operation; повтор текущего факта не меняет первоначальное время. DONE безSTART отвергается. Удалённый/чужой/включённый в счёт рейс недоступен. Dispatcher и driver используют один private store_fact существующего пакета. Товар/резервы не изменяются. Время сохраняет прежнюю DATABASE_LOCAL_DATE семантику; промышленная синхронизация часов не заявлена.

Checkpoint000spec/body/INVALID=[], rollback восстанавливает код без удаления истории. Полный snapshot базы не нужен. Применение и actual evidence ещё ожидаются.

## Installed1326
Миграция применена в RABAEV/orcl, USER_ERRORS=[], INVALID=[]. [B03 результат](../components/nicora_b03_driver_delivery_20261014.md), report46. Runtime mirror обновлён. Ранее указанный PREPARED — история подготовки, текущий статус INSTALLED / AUTHOR_DEV_CASE.
