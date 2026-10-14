# NI03.3: фактическое завершение волны

049 APPLIED в RABAEV/orcl, новый RRL_STOCK_WAVE_FINISH_CMD и Root posting VALID. [[nicora_ni033_fullpal_20261009]], [[nicora_ni032_target_supply_20261009]].

GET /api/picking/waves/{id}/execution показывает существующие PT/RT/warehouse/CASE/HARD и причины: незавершённый физический отбор, непокрытый факт/утверждённая недостача, контроль/отгрузка CASE, отсутствие фактической связи отгруженной СТ, активный резерв. Количества разных SKU/UOM не суммируются в общий товарный итог.

POST finish-execution → WAVE_EXECUTION_FINISH через RRL_STOCK_POSTING_API. DONE означает завершённый исходящий поток выбранной волны: PT разрешены фактом и при применимости утверждённой недостачей, ненулевые физические места связаны с SHIPPED fulfillment/APPLIED shipping provenance, физические/пополняющие задания закончены, собственного активного HARD нет. Подготовленная СТ не является отгрузкой. Отменённая потребность без явного решения не скрывается DONE.

Snapshot hash и полный ordered row closure PT/RT/WH/CASE/FF/HARD/wave проверяются под root locks/policy fence. Статус, журнал и outbox фиксируются вместе; P/H не меняются. Утерянный ответ повторяется user/API-scoped сохранённым body/ID. Панель добавлена в существующий wave-replenishment ARM. Более200 PT/1200 snapshot items требуют разбивки волны.

Реальный private case: finish до PICKING_MOVE запрещён; PAL3 → binding ST0.125BOX → SHIPPED BASE3; второй собственный PAL3 сохранён и блокирует finish активным HARD. После явного освобождения отдельного fixture HARD finish→DONE и exact replay passed. Сохранена история, очищены только private P/H. Это не подтверждение всех CASE/quality/short/multi-place вариантов.

SQL: snapshot53s6b519ntph3 ~18.92ms/2, fulfillment lookupdzqh55h01zmrr ~3.08ms/6. Решение inventory: scoped wave/owner/provenance и существующие ключи, no speculative index. Браузерная/независимая приёмка открыта. Следующие связанные задачи: общий CASE→control→shipping flow и NI04 warehouse composition.
