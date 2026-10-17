# Inventory task: назначение аудитора и scoped пересчёт

Статус dev APPLIED, программная бизнес-приёмка shortage→claim→count/replay PASS. Остаток блока1 после [[retailcase_assembly_scoped_execute_20261016]]. Весь блок прав ещё не закрыт.

MIGRATION_ID `2026-10-16-inventory-task-scope`; [SQL/rollback](../../db/migrations/2026-10-16_inventory_task_scope/README.md), [before sources](../../reports/retailcase/2026-10-16/inventory-task-scope/before/manifest.json).
Frozen manifest SHA `2b422ef4cebd4c0f7cced63649a4146c537b9fd917e2ef178948e97a0288c020`.

## Граница изменения

Новый `RRL_INVENTORY_TASK_ACCESS` владеет metadata claim. До и после REV/CONFIG/task/actor locks проверяются оба полномочия `inventory_task_execute` и `stock_inventory_count` на фактический WARE и текущего назначенного аудитора. SELF не покрывает неназначенную задачу; WARE/GROUP допускают claim. Чужое назначение/закрытое задание отвергаются.

Scoped пересчёт допускается только по IN_PROGRESS заданию текущего аудитора, его складу, ячейке и артикулу; DONE допускает лишь повтор исходного COUNT_OPERATION_ID. Само количество, маркировка, состав списка партий, stock version, источник shortage, текущая сессия/квалификация и восстановление остаются за прежними `RRL_STOCK_INVENTORY_CMD`/`RRL_STOCK_SHORT_RECOVERY`. Общий root повторяет native authority до replay и после блокировок; INVENTORY_COUNT добавлен к REV fence.

Legacy standalone count сохраняет flat stock_inventory_count и homeWARE/GLOBAL_ADMIN. Legacy task/count ветви сохраняют прежние инварианты. Дополнительная scoped роль не превращает flat count в глобальное разрешение чужого склада.

Чтение партий и marking profiles выполняется с native authority в одном READ ONLY snapshot; task-bound SELF требует точную ячейку/артикул. Нельзя применить task_id к произвольному содержимому склада. Лимит200, выборка201 обнаруживает превышение. Claim возвращает проекцию в исходной UOW, без нового read permission после commit.

Создание ревизии и lot birth HTTP пока сохраняют flat gate. SELF пересчёт использует заранее подготовленную ревизию своего склада; UI задачи/ревизии требует следующего отдельного metadata owner, если необходимо создавать ревизию самим назначенным аудитором.

## Проверка и восстановление

23 focused Python tests PASS: native boundary, identity, task bounds, отказ до проекции, одна read snapshot, прежние14 queue checks. Общий quality gate PASS: архитектура1097/0циклов/debt72,tooling24,оба TypeScript. Native OracleApply завершён; отдельное [readback](../../reports/retailcase/2026-10-16/inventory-task-scope/root-readback.json) подтвердило8 SHA, ledger APPLIED, ERROR/INVALID0, legacy admin read и3 inactive actor negatives. API перезапущен serv.bat без reload. Это ещё не положительный inventory/count сценарий.

Before включает6 exact native sources, включая root и lock implementation. Пакеты дополняются без новых таблиц или stock writer; source guards и code checkpoint включены в manifest. Rollback восстанавливает три прежних body и удаляет stateless helper; историю, остатки и назначения сохраняет, scoped-only действия перестают проходить.

## Фактическая приёмка

Свежие CASE1141/SHORT23/INVENTORY27/лот IQ16.LOT:26c2f13302; прежняя ASM1140 и её партии защищены exact snapshots. Отдельный picker сообщил0/недобор1, admin принял RESTORE, создано WAIT_INVENTORY. Старт без booked тары был отклонён; использована отдельная имитированная тара, исходная ASM booking сохранена. У уже назначенной CASE выпуск этикетки отклонён; внутренний идентификатор сохранён, физическая этикетка/подбор не заявлялись.

- [15 HTTP /11 ACL receipts](../../reports/retailcase/2026-10-16/inventory-task-scope/acceptance.json): positive inventory/recovery rows, отсутствие одного из двух прав, SELF на неназначенном задании, GROUP claim с homeWARE1 на actualWARE20220394, повтор claim, чтение партий, чужая ячейка403, удаление/возврат членства, quantity count и exact replay, изменённое тело409, отзыв/повтор403.
- До count commit canonical execute проверен caller rollback: собственный остаток1→0, inventory DONE/новое replenishment в TX; после rollback исходный снимок точен. После commit COUNT_OPERATION_ID сохранён, один журнал, old ASM exact. Count0 — имитированная тестовая потеря1EA, не физическая инвентаризация.
- [SELF + два соединения](../../reports/retailcase/2026-10-16/inventory-task-scope/rights-lock-reset-contract.json): assigned SELF lots/replay200; exclusive REV останавливает root на5034мс/ORA54; после release/reset_connection exact replay проходит. Первый raw harness пропустил обязательный root reset_connection после ошибки и получил DIRTY_TRANSACTION; его [исходный отчёт](../../reports/retailcase/2026-10-16/inventory-task-scope/rights-lock.json) сохранён. Production StockPosting UOW уже исполняет этот reset-контракт, native защита не ослаблена.
- [SQL после retirement](../../reports/retailcase/2026-10-16/inventory-task-scope/sql-review-after-retirement.json):19 HTTP/native/local пар (включая оба lock harness HTTP), max258мс,6 TX/denial records; top10 cumulative не p95. Решение — сохранить task/revision/cell/article guards,200/100 bounds и READ ONLY snapshot; inventory owner измеряет per-WARE/recovery планы на пилотном объёме перед индексами/cache. Намеренный REV wait не считается долгим SELECT.

[Retirement](../../reports/retailcase/2026-10-16/inventory-task-scope/retirement.json): own empty CASE/wave/plan отменены через canonical owner, inventory27 DONE и loss/access журналы сохранены; дополнительная тара отменена, баланс physical1/assembly1 исходной ASM сохранён. Новые3 пользователя DELETED, picker resource inactive/qualification0/session CLOSED, role/group inactive, grants revoked. [После retirement old ASM exact и INVALID0](../../reports/retailcase/2026-10-16/inventory-task-scope/protected-after-retirement.json).

Не закрыты аппаратная/независимая приёмка, manual inventory источники вне прежнего CASE-short owner, task-bound создание ревизии, additive legacy-flat+foreign-role matrix и остальные права/решения блока1. Не восстанавливать завершённую фикстуру для новых сценариев.
