# Единственный товарный эффект и read-only sync,147

Original native task command atomically sets physical effect/domain status/SYNCED. Python WarehouseTaskDomainSyncService._explicit_sync already verifies this committed proof in ACTIVE. PREPARED legacy retry executor is obsolete after owner-approved full cutover.

Remove PREPARED escape and exclusively unreachable Python domain-effect/replenishment event/reservation writers. Keep original sync list/detail and retry/dispatch interfaces; retry reads native proof or refuses TASK_POSTING_REQUIRED, never creates journal, changes stock, reserve, MES or wave effect. Release inactive fails503. No root compatibility switch changed.

Remove only call-free public wrappers and two exclusively-used obsolete infrastructure modules after reference inventory. Native SQL helpers and compatibility trigger remain existing authorities. Existing ordinary task829 replay sync serves real proof; inactive and missing native proof meaningful refusal cases. No history deleted.
