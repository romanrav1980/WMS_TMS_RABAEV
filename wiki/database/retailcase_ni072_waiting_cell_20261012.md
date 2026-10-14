# NI07.2: ячейка ожидания перенесённых СТ

## Реализовано, checkpoint763

В существующую RRL_RECEIPT_WARE_SETTINGS добавлено nullable поле DEFER_WAIT_CELL. Настройка доступна в существующем PUT /api/receiving/warehouses/{warehouse}/settings и форме receiving.html. Отсутствие поля в запросе сохраняет настройку; явный null очищает её. Настройка сама не переносит товар и не создаёт движения.

Oracle trigger RRL_DEFER_WAIT_CELL_GUARD проверяет существование ячейки того же склада, отсутствие OTBOR/IS_SYSTEM, запретов приёмки/остатков/пополнения и EXPEDITION_GROUP. Ячейка вне TRANSPORT_STAGING/GATE/FILM_WRAP последней опубликованной топологии. Ограничения вместимости, температура и актуальность назначения должны повторно проверяться при планировании и проведении будущего задания; текущая настройка этого проведения не заменяет.

[Миграция](../../db/migrations/2026-10-12_ni072_waiting_cell/apply.sql), [откат](../../db/migrations/2026-10-12_ni072_waiting_cell/rollback.sql). После добавления поля перекомпилированы зависимые RRL_STOCK_QC_POLICY и RRL_SSCC_ALLOCATOR; USER_ERRORS и INVALID пусты.

## Проверено на dev RABAEV

Case762: сохранение собственной metadata ячейки DW753, rollback настройки, отказ для неизвестной ячейки и ячейки отбора, затем commit назначения. Исходная паллета context744 сохранила P3/H3 в DP744. Case не переносил товар и не создавал новые маркированные единицы.

JS syntax receiving.js PASS. Quality gate763 PASS: 24 tooling/architecture tests, оба TypeScript проекта; architecture682/0cycles/76debt. Encoding764 PASS. UI браузером и оборудование в этом случае не проверены.

## Следующий функционал

Typed источник ST_DEFER в существующих RRL_STOCK_TASK_PLAN/CORE/DOMAIN, связь задания с latest RRL_ST_DEFER_DECISION и исходным fulfillment, штатный RRL_STOCK_TRANSFER_CORE.move с переносом HARD и маркированных единиц. Original DONE picking task/FACT_QTY не переписывать. Не разрешать общий MANUAL PUTAWAY. Перед проведением повторно проверять текущий склад, настройку ячейки, состав/резерв, принадлежность СТ рейсу и отсутствие LOAD/CASE/nested/frozen onward источников.

Исходники шести native пакетов сняты read-only capture760 в локальный tmp; это материал следующей миграции, не применённый новый handler. Все спринты ещё не завершены, публикация пока не выполнялась.

## Checkpoint770

API перезапущен штатным serv.bat (767), startup завершён. Actual HTTP769: GET выбранной ячейки и PUT без optional поля сохраняет DEFER_WAIT_CELL. Browser UI/hardware не проверены.

SQL guard: SQL_ID 65cv6415xmqp8, 4 выполнения, среднее 10.416 мс/188.3 buffers (768). Решение владельца transport/inventory: сохранить проверку одной ячейки и current published topology; перед массовым планированием профилировать lookup последней topology и индексы WARE_ID/CELL, не запускать эту конфигурационную проверку на каждую сканируемую единицу. Это проверка изменения настройки, не массовый stock writer.
