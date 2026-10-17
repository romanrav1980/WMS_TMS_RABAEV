# Независимая приёмка UTC-журнала операций

15.10.2026 — live Oracle PASS, 8 проверок. Миграция [[retailcase_stock_operation_clock_20261015]] APPLIED, INVALID0; исходники обоих trigger совпали с migration-файлом по содержимому без пробелов. Доказательства: [runner](../../scripts/stock_operation_clock_smoke.py), [отчёт](../../reports/retailcase/2026-10-15/stock-operation-clock/report.md), [JSON/checkpoint](../../reports/retailcase/2026-10-15/stock-operation-clock/native-report.json).

На изолированном назначенном задании WAVE395 выполнены настоящие prepare/execute в caller-owned транзакции. APPLIED создал ровно одну clock с исходными actor/kind, ORACLE_SYSTIMESTAMP, нулевым UTC offset и временем между двумя чтениями часов Oracle. UPDATE/DELETE отклонены. Caller rollback удалил операцию и clock; физический остаток, hard reserve и stock version восстановлены точно.

Исходный committed canonical replay вернул прежнюю квитанцию, изменённый запрос отклонён, отзыв текущего допуска запрещает replay. Старой операции clock не добавлен. Количество операций 5021, clock 0 до и после: положительная clock наблюдалась внутри откатившейся транзакции. Временные metadata и grants удалены, исторический QA-пользователь восстановлен, access audit сохранён.

Свежий slow SQL максимум 267мс; replay73мс, новых записей выше500мс нет. Решение — оставить адресное чтение PK/fixed fixture IDs; дополнительный индекс без измеренной потребности не нужен. Это функциональная проверка, не нагрузочное испытание.

Первый запуск runner завершился ORA-01745 из-за bind `:start` в проверочном SELECT; caller rollback и cleanup выполнены. Исправлено имя тестового bind, рабочий migration SQL не менялся.

Запись означает наблюдение APPLIED внутри TX, не COMMIT и не физический подбор. Синхронизация Oracle clock остаётся эксплуатационной задачей; исторические TIMESTAMP без пояса не пересчитаны, знаменатель KPI не выбран этой проверкой.
