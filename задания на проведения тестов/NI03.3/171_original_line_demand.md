#171: точечная оригинальная потребность

Запустить scripts/ni033_line_demand_existing_case.py при неизменённых исходных QA stock/orders. Доsnapshot сохранён tmp/ni033_pool_before171.json: два склада/8 строк. Проверить полное равенство прежнего pool, включая порядок/quantity/HARD/picked/overlap и форму JSON. По каждой строке targeted line helper даёт те же поля и BASE.

Quantity означает UNALLOCATED_BASE_NOT_SHIPPED_PROOF, не количество доставленного товара. Несколько профилей маркировки не умножают physical qty; cancelledPT не вычитается как current picked. UNIT_CODE/policy отсутствует → явный отказ, не EA по предположению. No stock/plan/order writes.

Независимая marked/partial/other-wave topology ещё не заявлена. Full pool N+1 остаётся bounded2000 и требует batched aggregation перед промышленным увеличением окна; targeted helper не должен вызывать полный stock/pool scan.
