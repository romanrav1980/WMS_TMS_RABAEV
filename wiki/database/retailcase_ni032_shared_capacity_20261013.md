# NI03.2: физическая вместимость общей подачи

Migration ID:2026-10-13-852-ni032-shared-capacity. Подготовлено до применения; live source851 captured/SHA/paired rollback. Владелец inventory, authoritative RRL_STOCK_REPL_CAPACITY; без изменения запаса/публичной сигнатуры.

Partial shared-owner850 выявил, что несколько logical replenishment rows одной целой паллеты одновременно занимают projected volume. Вместимость должна считать одну физическую FULL_PALLET на UID/source-cell/target-cell. BASE задачи остаются отдельными. Уже прибывшая source reservation не считается новым incoming; её физический запас учитывается в occupied.

При проверке прибытия исключается весь matching FULL cohort указанного RT, не только один logical row. Whole quantity берётся из текущего физического REMAIN; для weighted FULL используется прежний physical_volume, для BASE сохранён reservation_volume. Требования совпадающего source UID/cell/active HARD и существующая native shared-owner admission сохраняются; разных target здесь нет, reader задан одним p_cell. Нет освобождения склада, нового stock writer или решения государственного сервиса.

Проверить compile и свежий partial shared-owner: first whole arrival2+4, remaining6+4, requeue old unissued owner, one second physical12/shared third2, true capacity refusal and replay. Weighted FULL branch independent evidence remains open. Все собственные failed850 данные очищены finally; failed attempt не passed. [SQL](../../db/migrations/2026-10-13_ni032_shared_capacity/apply.sql).

## Применение и результат856

852 применена, native compile ERRORS[]/INVALID[]. Свежий850 после исправления QUEUED helper: tasks1096/1097 DONE20/12, owner12/other8/third14, exact replay и own P/H cleanup. Второй canonical task принадлежит rt1603, исходный continuation rt1604 использует ту же физическую подачу. Свободное целевое количество уменьшает intermediate remaining другого заказа4→2; общий резерв8 сохранён. Это developer evidence, weighted branch/независимая маркированная конкуренция открыты.
