# NI03.2: последовательные оставшиеся источники

Migration ID: 2026-10-13-834-ni032-sequential-sources. Подготовлено до применения. Владелец inventory; authoritative rule — прежний RRL_STOCK_WAVE_CMD. Единственная транзакция запасов/резервов/outbox — RRL_STOCK_POSTING_API.

Расширяется существующая partial target replacement: target4 при собственных bindings6+6 оставляет source2+6. Первый источник подаётся целиком обычным заданием. Следующую потребность вычисляет уже установленный RRL_STOCK_REPL_CONTINUATION по HARD владельца в целевой ячейке, а не по массе всей привезённой паллеты. Новый движок/параллельные задания не создаются.

Неизменённые bindings сохраняют количество и версии; release0 не вызывается. В закрытии ресурсов остаются все старые источники и резервы, executor перепроверяет каждый original binding даже при нулевом освобождении. Допуск целой первой паллеты по вместимости прежний; следующая подача проходит тот же планировщик после подтверждённого движения. Другой владелец HARD сохраняется. Несколько оставшихся bindings на одном выбранном UID/cell требуют отдельной точной схемы поступления и отвергаются.

Сохранён текущий live source833, SHA checkpoint и paired rollback. [SQL](../../db/migrations/2026-10-13_ni032_sequential_sources/apply.sql). Проверить свежий частный dev источник: отказ вместимости, rebind2+6, сохранение второго владельца, физическое продолжение/outer rollback/replay и compile. Старые factory632/protected source773 и20/20 не запускать повторно. Полный NI03.2 не закрывается этим slice.

834 APPLIED/USER_ERRORS empty/INVALID empty before case. Fresh835 refused before rebind effect because canonical positive-only quantity parser received zero release; original root rolled back and finally cleaned own P/H.836 private release_amount admits only canonical generated0 and delegates positives to existing exact math. Reapply/fresh case pending; no acceptance claim.

## Фактический835–837

После836 свежий случай835 PASS: target4 + own6/6 → targetH4/sourceH2+H6; первый whole20 доставлен прежним TASK_COMPLETE, сохранён other-owner8. Прежний REPL_CONTINUATION создал next demand6, reconcile использовал свободный товар в целевой ячейке, original second source8/H0 остался физически на месте. Итог target own12 + other8. Точное повторение rebind и physical move вернуло исходный результат. Все собственные остатки/резервы в finally очищены только штатным ядром; native taskDONE20/history сохранены.837 USER_ERRORS/INVALID empty, own P/H0.

SQL837: old shared owner reader34.274мс/268buffers, old source candidate32.93мс/502, release face40.719мс/213. Решение inventory: сохранить bounded201 и ordered closure, новый индекс без ухудшения плана не вводить; before industrial volume проверить планы этих legacy readers. Native direct calls не являются browser/аппаратной либо независимой приёмкой. Отказ вместимости и второй фактический источник после исчерпания свободного target требуют отдельных адресных случаев, не объявлены passed.
