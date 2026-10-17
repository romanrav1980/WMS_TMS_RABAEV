# Scoped EMPTY_TARE for ordinary CASE — 2026-10-15

Status: **APPLIED by root:9 statements,0 errors; four sources exact, INVALID0**. Author did not execute DDL/API/ACL. Root owns fixtures and runtime acceptance.

The current scoped operator can execute ordinary CASE quantity commands and CLOSE, but the warehouse scale request owner still used flat legacy rights. This increment adds only own ordinary `EMPTY_TARE` admission. It creates no table, grant, stock writer or new capture DTO.

The migration changes `RRL_WH_WEIGH_REQUEST_API` and `RRL_CASE_RESOURCE_POLICY` package bodies. Both specs remain unchanged. The resource policy accepts explicit `EMPTY_TARE`; it does not broaden `REPORT`. The new branch requires current scoped authority on the actual warehouse, current CASE assignee, zero picked quantity, active actual session/shift/resource/equipment/qualification, and released wave. Existing identifier, pallet type, device, sender, calibration, request/claim/zero/sample/window checks remain authoritative.

Task and candidate device assembly states `OPEN`, `BLOCKED` and `HOLD` deny new scoped EMPTY. Historical status uses current assigned authority and original frozen warehouse, without pretending the original content/session remains fresh. Legacy and `PICK`/`FINAL_GROSS`/ASM branches are retained.

Rollback requires exact installed sources and the unchanged weighing-history baseline: four requests, five claims, zero zero-progress rows and77 captures. Any new history requires forward recovery. Before/after guards hash CR-normalized `USER_SOURCE`; the source checkpoint separately retains exact raw hashes. The first failed baseline collection used a PL/SQL package constant in SQL; the root-run collector was corrected to resolve that constant through PL/SQL OUT and bind its actual value. Original evidence is retained.

Evidence:

- [Prepared migration](../../db/migrations/2026-10-15_warehouse_empty_scoped/README.md), [frozen manifest](../../db/migrations/2026-10-15_warehouse_empty_scoped/manifest.json).
- [Fresh source checkpoint](../../reports/retailcase/2026-10-15/warehouse-empty-scoped/before/manifest.json), [read-only history/device baseline](../../reports/retailcase/2026-10-15/warehouse-empty-scoped/history-before.json).
- [Prepared root-only OPC driver](../../scripts/warehouse_opc_native1939_empty.py): retained pinned TEST server, actual zero then actual0.5 observations, immutable bundle and raw binding; no hardware or quantity claim.
- [Staged acceptance plan](../../reports/retailcase/2026-10-15/case-scoped-close/n1939-empty-close-plan.md).

Actual root acceptance: encrypted TEST OPC requestB ? genuine zero confirmation ?0.5kg EMPTY capture ? raw evidence MATCHED. The subsequent ordinary1EA CASE pick under GROUP-only current authority passed inside caller rollback, with native flat rights0 and canonical ACL restoration through new assignment IDs. No quantity commit or positive CLOSE is claimed. Additional revoked/foreign/scans/resource/session/HOLD denial matrix, historical exact replay, legacy regression and slow-SQL decisions require their own evidence. A positive scoped CLOSE cannot be chained after an uncommitted stock transaction; it needs a separately reviewed canonical commit and compensation plan.


## Actual TEST evidence and clock boundary

- [Root apply](../../reports/retailcase/2026-10-15/warehouse-empty-scoped/root-apply.json), [independent source readback](../../reports/retailcase/2026-10-15/warehouse-empty-scoped/independent-readback.json).
- [First zero rejection](../../reports/retailcase/2026-10-15/warehouse-empty-scoped/first-zero-failure.json), [producer diagnosis and correction](../../reports/retailcase/2026-10-15/warehouse-empty-scoped/producer-zero-clock-diagnosis.md). Original request/claim/zero event remain preserved. Native correctly rejected actual OPC timestamps20?25ms preceding server claim creation. The producer now rereads genuine zero until observed_at and all seven DataValue server timestamps are within the claim window before durable staging; no timestamp rewrite or native relaxation.
- [Actual requestB capture](../../reports/retailcase/2026-10-15/case-scoped-close/empty-1939b.json): capture54242B33CD51447FC75059C28DA86D5ED46FA8ED2533D22776A8109E9D874B49, measured2026-10-15T18:04:03.355478Z, actual TEST0.5kg; raw MATCHED, original source unchanged.
- [Actual GROUP-only caller-rollback proof and ACL restoration](../../reports/retailcase/2026-10-15/group1939/group-quantity-journal.json). Original WARE/SELF grants remain revoked; restored effective scopes use N1939.GQP.RESTORE.WARE/SELF, with original validity retained. These are software TEST facts, not physical hardware acceptance.

The history baseline is now changed by actual requests/claims/zero/capture; the migration's original rollback guard must refuse restoration. Recovery is forward-only. Fresh tare freshness is judged against native measured_at, never extended by retries. A prepared requestC driver does not constitute a successful new capture or permission for a goods commit.
