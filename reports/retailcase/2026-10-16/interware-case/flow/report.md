# Mixed CASE tree: warehouse -> second warehouse -> store

Author verification on isolated dev TEST data; not independent or hardware acceptance.

CASE1145: ASM_FINAL1EA. CASE1146: BOX24EA + each-pick1EA. Same three original stock UIDs,26EA, one top handling unit. First trip33651, interwarehouse receipt at WARE30846272, one whole-HU placement task, second trip33652, PAPER_COUNT store acceptance26EA. Original CASE/ASM/ST/fulfillment and source tare histories retained. Original identifiers resolve to the received physical carriers. Source and target stock P/H0. Original orders:1/1 and25/25, no unattributed/unreceived quantity. Protected prior fixtures unchanged.

- [Caller rollback, commit, replay/conflict and identifier resolution](receive-readback.json).
- [First shipment and manual CASE weight proofs](load-top.json).
- [Placement/custody/onward metadata](onward.json), [second departure](onward-resume.json).
- [Store receipt and original order projections](store-readback.json), [HTTP receipts](store-v2.json).
- [Temporary identities retired, waves577/578 DONE](retirement-final.json).
- [SQL review35 exact HTTP pairs/max1686ms](sql-review-final.json).
- [Root verification of Claude UI](../root-ui/recovery_result.json).
- [Manual QC UI/exact retry](../../manual-warehouse-qc/ui/report.json).

The empty outer BOX was explicitly detached using existing HU commands. Native closest-box coverage still prevents double independent weight coverage by parent BOX and child CASE. Universal nested BOX manifests, partial subtree store handover, remaining scoped-write/concurrency matrix and hardware pilot remain open. Two source HELD tare books are retained; no implicit transfer of tare ownership.

All intermediate rejected commands and harness failures are retained. Runtime ORA-40573 was corrected through a separate guarded scalar-bind migration. Store custody is released atomically by STORE_RECEIPT; a separate repeated release is correctly rejected without another effect.

Combined architecture gate, both TypeScript projects,24 architecture/tooling tests,9 focused manual QC/origin tests and admin production build PASS. Existing leaflet/chunk-size build warnings remain. Recovery positive states are browser fixtures; live checks cover empty/403. No GitHub publication.
