#172: смешанная волна с сохранением факта и потребности

Существующий source tmp/ni033_mixed172_fixture.json: wave403, fullPT1911/task839/order1929, emptyCASE1038/PT1912/order1930. Metadata подготовлена синтетически (LAUNCHED precondition); actual native task/quality/shipment/cancel/finish выполнены. Это не SAP/auto-launch/real hardware/driver acceptance.

scripts/ni033_mixed_wave_existing_case.py повторяет прежние OP receipts; не сбрасывает DONE/SHIPPED/CANCELLED. Initial first-time proof: full3 move, independent KRO required item_scans3 + weight12kg/current policy4kgEA, actual SHIP by dispatcheradmin; emptyCASE1 cancellation; all-returned mode denied; mixed late rollback/fresh concurrent one durable receipt; current source rows quantity0/1. Own remaining source quantity cleared native count only after DONE, original P20H20 retained.

Проверить новый mode PARTIAL_SHIPPED_RETURNED/reason/currentactorWARE/rights. Нельзя обходить DONE task без SHIPPED provenance/непокрытый факт/activeHARD/неотменённый CASE/pending physical/replenishment/tare. Simple entirely returned mode должен остаться strict; freshMixed требует иDONE иCANCELLED.

Следующий существенный кейс: одна исходная строка заказа4, full3 shipped + separateCASE1 cancelled, current unallocated1 без стирания SHIPPED3. Marked/nested/multi-SKU/UOM отдельно, без ложного суммирования. API DTO/403/immutable retry/UI pending mode and reason. Native current SQL/VALID evidence, bounded200/1200; no industrial-load claim.
