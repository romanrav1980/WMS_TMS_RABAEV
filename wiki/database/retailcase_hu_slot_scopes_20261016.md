# Области исполнения слотов, упаковки и распаковки HU

Статус dev APPLIED/5SHA/ERROR0/INVALID0. Migration `2026-10-16-hu-slot-scopes`, frozen SHA `96b6bde549c31c93ac3028643d35289fb9adc176ca04514e566370baa29e25f5`.

Пять package body-only изменений: `RRL_HU_EXEC_ACCESS`, прежние SLOT_MOVE/REPACK/UNPACK owners и Root. Текущие исходный/дочерний склады проверяются до rich compile и cached replay, затем повторно под REV/config/physical locks. SLOT для STOCK допускается только из одной фактической ячейки; CASE — по фактическому складу CASE; container — по current cell. Контракты same-cell slot/capacity, scan/version/measurement и CASE booking не снимаются. Количество двигают прежние owners.

REPACK сохраняет legacy home/global ветку и добавляет current WARE/GROUP роль; NULL home/group не считается разрешением. Read-only slot каталог, геометрия, занятость, замена claims и проверка целого места остаются прежними. В API unpack/relocate/repack вход identity-only, native принимает решение по фактическому источнику. SELF-only access и shipping/finance этим инкрементом не объявляются закрытыми.

SQL `db/migrations/2026-10-16_hu_slot_scopes`; before5SHA/INVALID0, exact source guards, verify, paired rollback. Новый HT16.c31efb0e6c прошёл назначаемые HU-перемещения, REPACK_SLOT, RELOCATE_SLOT, UNPACK:5EA сохранены в двух слотах225/226.12HTTP проверили replay/changed/foreign/исключение склада из GROUP; caller rollback восстановил links/версии/claims, второй connection подтвердил REV fence ORA54. Результаты `reports/retailcase/2026-10-16/hu-slot-scopes/{acceptance-v2,http-matrix}.json`.

SQL review:63 фактических HTTP/audit pairs, максимум1128мс,11 slow rows; `sql-review-final.json`. Сохраняются bounded KPI31день/лимиты и native locks. Inventory/transport owner до пилотного объёма проверяет планы loading prepare/admission и warehouse JSON extraction; cumulative V$SQL не выдаётся за p95. Нативным вызовам не приписаны HTTP request IDs.

См. [[retailcase_hu_task_scopes_20261016]], [[retailcase_hu_scoped_execute_20261016]].
