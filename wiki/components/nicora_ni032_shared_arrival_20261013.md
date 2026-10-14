# NI03.2: одно задание общей целой паллеты

Основа — прежние RRL_STOCK_REPL_SHARED, RRL_STOCK_REPL_NEED, TASK_COMPLETE и sync_wave_tasks. Владелец физических заданий resources, логического ожидания inventory, запись количества только RRL_STOCK_POSTING_API. Новых таблиц нет.

Свежий840 выявил два одинаковых физических задания одной паллеты для двух заказов после отказа вместимости/пересмотра.831–844 projection выделен в resources/infrastructure/wave_task_projection.py: один FULL_PALLET на UID/from/to/quantity в wave, только текущая source reservation/stock location, прежний shared-owner admission, запрет второго активного физического задания источника. BASE задачи не объединяются. Current actorWARE проверяется под прежним metadata CONFIG6.

Уже перемещённое shared HARD могло оставлять RELEASED placeholder с прежней source cell и дважды занимать прогноз вместимости. Inventory public helper снимает только невыданный FULL_PALLET placeholder, если исходный резерв фактически в target, прежний remaining_for_task=0 и нет physical task этого RT. STATUS=CANCELLED/demand0, причина сохранена; DONE/fact за чужое задание не выдумываются. Stock/HARD/units не меняются. Вызывается до continuation selection и физической выдачи под существующей metadata транзакцией.

846 ограничивает maintenance суммарно200 RT на склад; проверяет RUSERS warehouse, группирует выбранные IDs и повторно проверяет факты в UPDATE.847 mock PASS forbidden warehouse и201rows до любого UPDATE, выбранные IDs сохраняются. Не утверждать live positive именно нового ID-bound варианта: actual840 предшествует846, мутация846 уже, gate architecturePASS.

## Реальное исполнение840/845

Уменьшенная вместимость оставила source20/H14,source8/H6,target4/H0 без изменения. Затем valid rebind: targetH4/sourceH2+H6. Один physical task1086 доставил whole20, original continuation6 создан. Отдельная новая волна забрала свободные10 единиц; часть её резерва2 оказалась на втором источнике. Reconcile снял ложное ожидание первого shared arrival, затем ровно одно задание1087 доставило whole8. Итог original owner12/second owner8/third wave10, exact physical replay.845 native VALID, taskDONE20/DONE8, все собственныеP/H0 через штатную cleanup. Старые защищённые источники не изменялись.

HTTP task1087 200DONE; browser734 DOM8EA/fact8/remaining0/disabled. screenshot09 показывает очередь с выбранным1087, не весь detail card. Не аппаратура/независимое испытание. Failed earlier840 attempts были очищены finally; ошибки bound variable и диагностического builder не являются passed.

Gate845 PASS24/bothTS/architecture688-0-76/encodingPASS; pytest-cache rights warning explicit. После846 architecturePASS и targeted847, fullgate не повторялся. SQL shared maintenance17.55мс/126buf и wave discovery26.163мс/84buf до846: retain bounded200/noindex, ownerinventory. SQL projection measurement still open (SQL_TEXT1000 prefix didnotmatch PALLET_RANK); do not claim measured. Partial shared consumer needing additional source/marked/independent races remain open.

## Partial shared856

Helper849 теперь обрабатывает RELEASED и QUEUED, только неизданный physical task с исходным own HARD уже в target. Zero remaining снимается без fake DONE, positive remaining возвращается в прежний selector с очищенной stale source binding. Фактический850: shared20+12, owner12/8/14, replay/owncleanup. Sum200 warehouse selection выполнен live; независимый reviewer/marked race ещё не выполнялись.
