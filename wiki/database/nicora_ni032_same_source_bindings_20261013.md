# NI03.2: несколько резервов одного источника

Migration866 подготовлена. Existing RRL_STOCK_WAVE_CMD сохраняет полный old_a всех own bindings, точные release_quantity/version/current owner и ordered stock closure. Старый отказ PARTIAL_TARGET_DISTINCT_RETAINED_SOURCE_REQUIRED убран: несколько retained reservation на одном UID/cell не означают несколько физических паллет.

Representative source сохраняет собственную BASE_QTY/version; не заменяется суммой чужих резервов. Все остальные own bindings остаются в original release/closure plan; whole TASK_COMPLETE использует существующий полный transfer план владельцев. Последующая remaining_for_task определяется по реально доставленному целевому резерву, не по одному representative id.

Нет объединения строк резерва, DML остатков, изменения public signature/stock writer. Current captured865 / SHA / paired rollback; fresh same-source positive, replay/rollback/native compilation ещё ожидают. [SQL](../../db/migrations/2026-10-13_ni032_same_source_bindings/apply.sql).

## Допуск869

866 applied VALID; fresh867 остановился до physical issuance, finally owncleanup. Старый RRL_STOCK_REPL_SHARED.allowed также запрещал несколько source bindings одного CASE owner.869 prepared: count=1 заменён sum(BASE_QTY) per current UID/cell/wave/line against remaining minus existing target HARD. Каждый distinct reservation проходит прежний warehouse/target/CASE/status/customer check; исходный полный ordered transfer closure сохраняется. Не объединяет reservations, не списывает чужой товар. Captured868/SHA/paired rollback. Повторный свежий case и live verification ожидают.

## План состава872

869 applied VALID; fresh867 выдал одно физическое задание, но execute_bind отказал CLOSURE_CHANGED до commit; own finally cleanup. Причина: pre-arrival target coverage excludes representative only; whole arrival одновременно переносит остальные own source bindings, поэтому post-target coverage увеличивается.872 prepared captures exact expected_target_covered = prior target + other own incoming only for whole PALLET. Runtime сохраняет equality check и остальные status/quantity/fact/owner guards. Root whole transfer closure captures all reservation identities/versions; no guard bypass.

Continuation whole PALLET subtracts sum of original own active HARD on same UID/fromcell, not only representative row. BASE unchanged. Потребность другого владельца не включается; нет fake continuation, если все own резервы прибыли. Captured870/871/SHA/paired rollback, live/fresh pending.

## Итог873–875

866/869/872 applied, ERRORS[]/INVALID[]. Fresh867 wave546/task1099 DONE20: two own source6/6→2/6 retain separate reservation identity; target original4+8=12, other8 preserved, next_rt=null. Root source and physical replay returned saved result. Own P/H cleaned through original commands. Failed earlier867 correctly rolled back before stock commit, not passed.

New related850 after872: two distinct sources20+12 delivered, original12/other8/third14, capacity refusal/exact replay/owncleanup. Context report873 retained separately; original report08 source1096/1097 remains historical and not overwritten. Current SQL projection13.588ms/125buf, requeue8.27ms/151buf, continuation2.677ms: bounded windows remain, ownerresources/inventory; noindex without slow evidence.

Marked/weighted branches and independent concurrency remain open. Removing count1 did not disable complete transfer/reservation/target equality guards.
