# NI05.1 F1 — storage identifier and recorded exemption

14.10.2026. RELEASE. Applied to the existing RABAEV/orcl dev database.

## Functional change

`002_reader.sql/exemption_json` now distinguishes whole unchanged native receipt from storage-only exemption. Storage-only requires the existing full-pallet fulfillment binding, completed PALLET picking task, immutable APPLIED TASK_COMPLETE movement retaining the physical identifier, exact full quantity/UOM/current target stock version. No second barcode registry. Missing or ambiguous binding refuses exemption. Existing marking, sample and CASE scale checks remain independent.

`004_gate.sql/status_json` adds `weight_exemption_recorded:boolean`, default false, matching current document and composition signature against immutable EXEMPT_FACT. It does not change shipping readiness: shipping records its audit inside its root transaction. The label API owned by root uses this field to refuse premature exemption labels. `007_exemption_lookup.sql` adds DOCUMENT_ID index; apply includes it before verify/ledger. Rollback intentionally retains this additive index.

## Actual native acceptance

Evidence: [native_fixture.json](native_fixture.json), [readonly.json](readonly.json), [recorded_status.json](recorded_status.json).

Own fixture f9734885e0: warehouse16447976, SKU QCF1.SKU.f9734885e0, physical pallet FULL.QA:f9734885e0, ST641516 / QCF1.ST:f9734885e0, order2140, wave561, task1168, fulfillment188. SAP supply858f6b6bdf2c4c178210cb6364952b48; receipt QCF1.RECEIPT:f9734885e0.

Actual SAP XML import and receipt3 EA → putaway → HARD reservation3 → native fullpal task completion → PICK_PALLET_BIND_SHIPMENT → storage-only rule (whole=false) → QC PLAN ready=true, exemption basis SCANNED_ORIGINAL_STORAGE_IDENTIFIER, immutable audit exactly1. Exact root replay returned identical saved result, including after cleanup. No physical shipping/loading is claimed.

Readonly negatives: no binding and fake binding denied; whole unchanged positive preserved; audit unchanged by reads. Recorded lookup: matching document/signature true, stale signature and wrong document false; cleaned fixture status returns false. Native compilation: no USER_ERRORS; all objects VALID.

Cleanup used stock root: own remaining P=0, HARD=0; own rule inactive. History retained. No B01/B02 or foreign stocks changed. Parent warehouse6524567 rule remains inactive.

## SQL and recovery

Binding query9x68xmh3daghj averaged4.762 ms across5 executions,140 total buffer gets. Existing binding keys adequate; no extra binding index. Audit lookup bounded by document and first matching row; new DOCUMENT_ID index avoids scanning the cross-document history. This is targeted evidence, not load acceptance.

Fresh reader checkpoint: before_reader.sql and checkpoint.json. Final reader SHA256: 5c49463bdb063838fb3bf5e2eef429ed3bdd145013b2ddc8a0b0ad1462e4cfd5.

The later gate checkpoint script failed an import before apply, while the PowerShell sequence continued. This is recorded explicitly: before_gate_reconstructed.sql is reconstructed from current USER_SOURCE by removing only the exact additive status patch; it is not represented as a fresh pre-apply export. The patch compiled and lookup evidence passed. Existing project migration rollback remains available.

Initial fixture continuation encountered a Python dict/LOB reader mismatch after successful QC PLAN. Cleanup still ran. The retained scripts now use read_oracle_json; final evidence independently read the APPLIED result/audit and performed exact replay. Fresh-case script includes the successful dedicated picking-reference cell layout. Do not rerun the historical resume script after cleanup.

No common gate repeated; root handles integration gate, wiki database/index/log and release summary.
