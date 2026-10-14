# NI03.3: одна исходная строка, отгрузка3 и остаток1

Ticket173, подтверждён обычный немаркированный вариант без нового движка/DDL. Исходные own order1931/row3416 requested4EA, один plan1908/line1909; FULL PT1913 qty3 + CASE PT1914 qty1. Wave404/task840/ST641322/FF83/CASE1039.

Подготовка source metadata синтетическая LAUNCHED precondition, не SAP/auto-launch acceptance. Далее реальные existing native команды: birth/full source3+CASE source2, HARD3+1, pickrelease, task move3, full binding, независимый KRO item-scans3 + weight12kg/current4kgEA policy, dispatcher shipment3, empty CASE cancel1, PARTIAL_SHIPPED_RETURNED finish. Wrong all-returned409, late execute rollback сохранил LAUNCHED, fresh concurrent one durable receipt.

FF83 SHIPPED3/MIXED173.SHIP сохранён. Native line_snapshot_json3416 quantity1, picked3, HARD0, requested4. Именно одна исходная строка, без второй строки/сброса факта/подмены shipment. Отмена CASE с другим PT в той же PL допустима; cancellation_shared_pick_task guard относится к общему PT, не общему источнику заказа. Original P20H20 сохранён; own leftoverCASE2 убран native inventorycount только послеDONE.

Sources scripts/ni033_single_order_mixed_fixture.py (relative tmp cache), ni033_single_order_mixed_case.py, tmp/ni033_mixed173_fixture.json. Повтор использует receipts, не повторяет initial H/rollback proof. Real hardware/SAP/Gov/driver и marked/nested варианты не подтверждены. NI03.3 остаётся открытым с residuals; это функциональный ordinary source-owner slice.
