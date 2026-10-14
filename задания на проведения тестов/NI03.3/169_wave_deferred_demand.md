#169: решение завершения возвращённой волны

Существующие author sources: scripts/ni033_wave_defer_existing_case.py (rollback на оставшемся own400, replay402), ni033_wave_defer_concurrent_case.py (existing401 receipt repeat), ni033_wave_defer_scope_case.py.

Не путать RRL_STOCK_NATIVE_API.post (сам COMMIT) с prepare_command/execute_prepared (внешняя транзакция). Проверка rollback использует только prepare/execute. Не сбрасывать completed401/402 назад в LAUNCHED. Новая concurrency401 уже подтверждена автором; текущий повтор проверяет старый receipt.

Пройти обязательную reason/одинаковый OP exact/другое содержимое409. Open395/unfinished physical/active HARD/non-returned CASE/current fulfillment должны отказать. Чужой текущий WARE отказывает до saved replay; возвращённый GLOBAL_ADMIN получает exact saved response. Перед новым изолированным concurrency-case изучить существующий fixture и не менять товары других сценариев.

Волна закрыта с completion_outcome UNFULFILLED_RETURNED_TO_PLANNING, order_fulfilled false; исходная потребность1928 остаётся1, исторический CASE1037 picked1 сохранён. Не выдавать такое закрытие за SHIPPED/SAP/GovACK. UI отдельное действие, причина, сохраняемыйOP и recovery; обычный ready gate сохраняется.

Проверить bounded200 исходных строк,1200items, currentOracleVALID/USER_ERRORS и длительныеSQL; сопоставить coldparse/повтор без заявления промышленной мощности. Partial mixed-wave lifecycle в этом режиме не реализован.
