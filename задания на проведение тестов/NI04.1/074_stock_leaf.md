# Qwen074: товарная паллета / пустая тара
Собственные fixture, P/H только root; scripts/ni041_stock_leaf_case.py исходный авторский сценарий.
1. Паллета P5/H2 вложена в тару; task place→unpack в отдельный слот; parent пустой, leaf P5/H2/owner unchanged/new slot, две task/claim/SYNCED, quantity journal0, replay.
2. Вывезти пустую тару без товарной проводки; existing whole INTERNAL_MOVE товарной паллеты освобождает old claim.
3. H-only не снимает измерение. P6→5 сохраняет новую comp epoch, old mass не принимается; fresh relocate-slot/remeasure восстанавливает размещение.
4. Marked unit membership replacement at sameP invalidates measured digest; multiple gov profiles do not multiply quantity.
5. Concurrent unpack/relocate/new arrival same slots: only one succeeds; capacity current+planned bounded; rollback has no partial task/claim/reserve change.
6. ARM scan identifiers accepts legacy internal pallet IDs; durable retry exact, rights/actor server; CASE child remains explicit unsupported.
7. Longest SQL explicit decision, only own cleanup, no full sprint acceptance without independent cases.
