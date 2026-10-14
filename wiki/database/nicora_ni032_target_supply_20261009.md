# NI03.2: существующий целевой запас вместо повторного пополнения

048 APPLIED в RABAEV/orcl; RRL_STOCK_WAVE_CMD package/body VALID. [[nicora_ni032_shared_supply_20261009]]. Команда существующая WAVE_RESERVE_SOURCES, transaction owner RRL_STOCK_POSTING_API; второй allocator/worker не создан.

## Атомарный эффект

Для explicit CASE с невыданной физической подачей команда может заменить полный собственный HARD хранения на пригодный свободный запас того же SKU/BASE в фактической ячейке отбора. P не перемещается. Старые HARD и их unit bindings освобождаются, новый HARD и точные unit bindings закрепляются за тем же заказом/PT. RT отменяется как уже обеспеченный; фактическая подача не создаётся. PT/WT отражают выбранный фактический UID/источник.

Eligibility включает warehouse, недоступные карантинные адреса, сроки/customer shelf, putaway/regulatory/composition. В подготовке закрываются ordered anchors всех старых/новых stock/HU/units/reservations/PT/wave и policy fences; исполнение повторно проверяет stock/reservation versions, владельца, потребность и отсутствие выданной физической подачи. Старый HARD освобождается и новый создаётся в одной root-транзакции с журналом/outbox. Любая ошибка откатывает целиком.

Ограничение текущего slice: суммарный полный собственный HARD хранения должен равняться недостающей target потребности; один пригодный фактический UID target должен покрыть этот объём. До200 собственных резервов. Деление физической единицы, частичный перенос набора и несколько target UID не предполагаются автоматически. Эти расширения остаются отдельными tickets.

## Продолжение и реальный сценарий

Существующий ReplenishmentContinuation теперь подбирает также первичные pending explicit RT: уже покрытые target, пригодный target free, собственный допустимый source либо новый свободный source. Он использует те же frozen intent, AlternativePickFaces и existing task sync. WAIT_MINIMAX до trigger не превращается произвольно в физическую подачу. Issued work не перенаправляется.

Реальный private case: own storage P/H20/20 (два заказа12+8), отдельно target supply20. При блокировке target P/H не изменяются. После открытия существующий reconciliation заменяет HARD12+8: storage20/0, target20/20; replenishment tasks0. Точные root retries возвращают сохранённый результат. Явный допуск и физический CASE12+8 завершены. Очищены только private P/H через root, истории сохранены. Это подтверждение стыка target supply; реальный полный MINIMAX production arrival/многопаллетный промышленный прогон ещё не объявляется проверенным.

MINIMAX/continuation worker перезапущен Hidden с новым кодом; runtime identity и stdout находятся в runtime/minimax_worker. Независимая/Qwen/browser приёмка открыта.

## SQL-решение

Новый deficit0wcq1grz8g53c ~17.68ms/9, bounded reconciliation5zdz0auz7ycv6 ~25.63ms/3 (отдельный initial parse99ms). Demand split13–24ms. Решение inventory: текущие wave/SKU/cell и окна200; оставить existing keys. Повторный разбор по plan/statistics/slow log при устойчивом росте≥500ms; масштаб не подтверждён.
