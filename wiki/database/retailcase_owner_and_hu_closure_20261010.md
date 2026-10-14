# Закрытие ресурсов: owner покрытия и ограниченный HU/волна

056 planned implementation, продолжает [[retailcase_ni032_target_supply_20261009]] и [[retailcase_ni041_hu_case_20261010]].

Покрытие конкретного PICK_TASK считается только HARD того же CUSTOMER_ORDER_ID, actual picking target и SKU. Резерв другого owner не уменьшает требуемую подачу.

Wave finish должен блокировать только fulfillment с подтверждённой provenance текущей wave, а не всю историю всех заказов. Число этих закрываемых строк ограничивается 200; превышение не изменяет статус и требует ограниченного разделения волны.

HU snapshot ограничивает также весь выбранный физический unit set 10000, суммарно по листьям, а не только 200 узлов/depth16. Это та же граница сканирования, без снятия unit locks. CASE строки перед повторным чтением состава получают реальные FOR UPDATE в порядке CASE_PICK_TASK_ID, после полного набора упорядоченных anchors/fences. Это дополняет общую сериализацию metadata CONFIG X и защищает от незавершённого чтения legacy row callers.

056 APPLIED, four package pairs VALID, checkpoints320–323. Target supply12+8/CASE, wave finish/shipment and two CASE-in-HU cases passed after replacements; own P/H cleanup done. Independent race and 10001-unit boundary cases not claimed. Existing metadata CONFIG X is retained; real CASE row locking takes sorted IDs through individual PK FOR UPDATE (Oracle does not permit FOR UPDATE over the union query).
