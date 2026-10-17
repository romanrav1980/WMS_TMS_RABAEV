# Независимое scoped согласование недостачи

Статус dev APPLIED/7SHA/INVALID0. Native positive/caller rollback/replay/rights/REV wait PASS; связанный дефект обычной инвентаризации исправлен отдельным dev комплектом/4SHA/INVALID0. ACCEPT_SHORT и свежая RESTORE регрессия приняты. Блок1/AK07: запрет самосогласования и текущие права согласующего.

MIGRATION_ID `2026-10-16-short-independent-scope`; [комплект](../../db/migrations/2026-10-16_short_independent_scope/README.md). Frozen SHA `4488fb53b7c8217992e9ef13d576c244589e43d1dbcc4812ef54ce2a86fbea15`.

Согласующий отличается от исходного `RRL_CASE_PICK_SHORT.CREATED_BY`, включая GLOBAL_ADMIN. Проверка прежним `RRL_ACCESS_API.assert_independent` проходит до replay и повторно под Root locks. Отсутствующий автор даёт отказ. READY означает готовность восстановления, а не новое согласование; его прежние проверки сохраняются.

Только `case_pick_short_approve` получает additive роль на фактический WARE CASE с серверным assignee для SELF. Legacy home/global сохраняется; flat на другом складе сам по себе не достаточен. Native writer повторяет текущий допуск. Root включает CASE_SHORT_APPROVE в REV-before-CONFIG fence, чтобы отзыв полномочий не опередил эффект/повтор.

Изменены3 тела,7 source guards; схемы количества/тары/stock/recovery и журналы не меняются. Парный rollback восстанавливает прежние тела. Author review не является независимой приёмкой. До закрытия требуются actual native/API positive, self/foreign/revoke/replay/lock cases и slow-SQL решение.

## Текущий native/API кейс

CASE1143/SHORT24/QA SQ16.bc4f60f03a: автор с legacy permission получает409 `INDEPENDENT_DECISION_REQUIRED` (существующий native error20851); foreign actor без роли/неверный WARE403, actual WARE role approve200/точный replay200/changed body409/revoke403; GROUP replay200/member removal403.10HTTP включают первый повторённый отказ стенда (ожидал403 вместо принятого conflict409). [Приёмка](../../reports/retailcase/2026-10-16/short-independent/acceptance.json). Two-connection REV exclusive вызывает ORA54 через5044мс; caller rollback возвращает decision/stock/new inventory к исходному состоянию, mixed tree26EA неизменно.5 HTTP boundary tests и quality gate PASS.

Только approve endpoint переведён на identity dependency; native authorizer решает допуск. Актор берётся из аутентификации. Нулевая short identity422, permission denial403, conflict409, uncertain503 с прежним operation_id. Legacy reject endpoint и прочие manager-команды этим инкрементом не закрыты.

### Блокирующий прежний дефект обычной инвентаризации

ACCEPT_SHORT создаёт task при AUTO_INVENTORY_ON_SHORT, но `RRL_STOCK_SHORT_RECOVERY.plan_inventory` требовал только WAIT_INVENTORY от RESTORE. Поэтому обычный task32 не мог завершиться. [Отдельный комплект](../../db/migrations/2026-10-16_short_accepted_audit/README.md), MIGRATION_ID `2026-10-16-short-accepted-audit`, frozen SHA `c19210d264eb1e1b40bb286a4c436a13c99df5341a793045872d97db4a52da16`, dev APPLIED/4SHA/INVALID0. Один owner body,4guards, paired rollback; существующий count/balance writer сохраняется. Новый ACCEPT_SHORT mode завершает только проверку и освобождает inventory session, без открытия SHORT_PICKED строки/пополнения; RESTORE переход сохранён.

[Task32 count/retirement](../../reports/retailcase/2026-10-16/short-independent/retirement.json): caller rollback/exact count replay PASS; тестовая потеря1EA отражена canonical inventory, task DONE, RECOVERY_STATE/REPLENISH_TASK_ID=NULL. Доступы/пользователи/ресурс/квалификация/смена SQ16 retired, журнал сохранён. CASE1143 закрыта WAIT_CONTROL, пустая, P0/H0. Её отмена/закрытие волны/отмена брони отказаны прежними guards `CASE_EMPTY_CANCEL_SHARED_OR_EXECUTED_PICK_TASK`, `WAVE_EXECUTION_OR_SHIPPING_PENDING`, `TARE_BOOK_CASE_PHYSICALLY_UNUSED_REQUIRED`. Бронь SQ16.TARE.BOOK HELD и третья TEST тара сохранены; исходные2 брони mixed-tree не менялись. **Отдельный backlog inventory owner: каноническое завершение полностью принятой недостачи с пустой CASE**, сохраняя DONE pick/short history и корректно освобождая тару; не заявлять полный retirement этой фикстуры, не делать прямой SQL-отмены/фиктивной отгрузки. Идентификаторы SQ16 никогда не переиспользовать.

[Свежая RESTORE регрессия](../../reports/retailcase/2026-10-16/short-restore-regression/regression.json): CASE1144/SHORT25/task33, отдельная TEST1EA. RESTORE → WAIT_INVENTORY → count0 → WAIT_REPLENISHMENT/1648, caller rollback и exact replay PASS. [Штатный retirement](../../reports/retailcase/2026-10-16/short-restore-regression/retirement.json): empty carrier return, WAVE_CANCEL/PICK_PLAN_CANCEL, book cancel и TEST tare count4→3; actor/resource/session/shift retired, histories retained, INVALID0. Эта проверка не переиспользует retired SHORT23/task27.

[SQL review](../../reports/retailcase/2026-10-16/short-independent/sql-review.json):10HTTP/10 Oracle-local пар/max188мс/0slow rows для этих HTTP; native count/rollback/retirement не получают выдуманные API пары. Решение: PK/currentWARE, bounded reservations, whole cell/SKU count и REV-before-CONFIG сохранить; owner inventory/access измеряет anti-join/task plans на объёме пилота. Общие V$SQL means не являются p95 этого кейса.6 HTTP boundary tests, quality gate1098/0циклов/debt72/tooling24/обаTS PASS. Независимая и аппаратная приёмка остаются открытыми.


## Empty CASE backlog resolved

The earlier CASE1143/SHORT24 retirement blocker is resolved by [[retailcase_empty_short_disposition_20261016]]: explicit native disposition preserves DONE/SHORT_PICKED/accepted-short/count history, cancels empty header, releases only own booking and retires own TEST tare; wave574 DONE. Previous failure reports above describe the pre-fix checkpoint. Mixed tree/two original tare bookings remain protected; no fictional shipment/state SQL.
