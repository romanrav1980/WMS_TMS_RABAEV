# Qwen: пополнение целой паллетой и категория B
Независимое задание; исполнение этих тестов не заявлено. Использовать только собственные dev fixtures в RABAEV/orcl. Не удалять чужие документы или journal; вернуть свой P/H через root. Не создавать новую схему.

1. Прочитать existing ABC_GROUP, RECEIPT_SKU_RULE.ALLOW_PICK_BATCH_MIX, REPL_ADMISSION, WAVE_CMD, TASK_PLAN/CORE, REPL_CONTINUATION.
2. Source100, demand50, capacity100: доставка целой100; для категории A не применять partial правило B.
3. B, target40/capacity100, demand20, source80: доставка60, source20. Demand20 остаётся отдельно от physical supply60.
4. Иная партия/expiry: отказ по умолчанию; флаг допускает только разные партии того же SKU в OTBOR=1. Другой SKU и storage mixing запрещены.
5. Source20/demand50: после факта один parent-linked child30. Нет источника → никаких новых HARD/WH задач. Поздний source30 → общий факт50. Повтор reconcile/confirmation не увеличиваетP/H/число детей.
6. Чужой HARD на целой исходной паллете: нельзя физически увезти чужой резерв. Проверить появление чужого HARD между планированием и подтверждением; отказ атомарный.
7. Для маркированного SKU перенести ровно фактические unit keys, сохранить оставшиеся на источнике; два профиля одной штуки не удваивают количество. Старый aggregate после partial не подтверждает прежний полный состав.
Зафиксировать вход, команды/operation IDs, факты P/H/unit identities, domain/status и существенные отказы. После meaningful case прочитать slow SQL и записать решение, без широкого нагрузочного прогона.
