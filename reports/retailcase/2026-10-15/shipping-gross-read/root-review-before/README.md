# SHIPPING_GROSS informational read candidate

PREPARED ONLY. Not installed/compiled in Oracle. No routes, captures, admission, QC writes or stock effect. This is a source candidate for independent/root review; it is NOT an executable migration kit. Before any DDL, root must add fresh before/after guards, strict verification, paired rollback, namespace/dependency/error/INVALID gates and ledger. Current source checkpoints live in reports/retailcase/2026-10-15/shipping-gross-read/{before,purity} and retain raw and normalized SHA separately.

## Native changes

New RRL_SHIPPING_GROSS_READ.freeze(source,server_actor,out). Existing source change only RRL_STOCK_HU_SHIP_CMD spec ACCESSIBLE BY adds that exact new trusted package. Its execute_command is not called. Existing body and shipping compiler are unchanged. No public arbitrary command/operation/actor is accepted in source. Source fields exactly handling_unit_identifier, scan_container, expected_root_version. Physical generic UID or unique SSCC resolves an existing CONTAINER in a real WARE/cell; top/closed/current version/leaf coverage/open tasks/existing per-ST QC are enforced by the reused compile.

RRL_ACCESS_API.assert_allowed(actor,warehouse_task_view,WAREHOUSE,actualWARE,null) is the existing current policy (WARE/GROUP/dynamic revocation included). No new flat fallback or warehouse-field rewrite is added. The owner policy's existing legacy/admin behavior is retained, not replicated. SELF alone with null owner cannot authorize the physical warehouse. No scopes/roles/grants are created by this increment.

RRL_STOCK_HU_SHIP_CMD.compile_command declares in-memory policies/resources and calls existing shipping compiler with skip_qc, then separately requires current child QC. We read its existing shipments domains and opaque compiler resource declarations, rather than inventing allocation/FF SQL. This first read therefore REQUIRES valid per-ST shipping QC; it does not permit using an outer weight to create that child QC. Supplier/interWARE cases retain all existing compiler restrictions. Source audit found DML only in execute/consume/record procedures, not invoked compile/declare/assert paths; actual read-only native acceptance remains required to verify transitive behavior.

## Consistent UOW and locks

Python ShippingGrossNativeRead takes a dedicated connection factory. First transaction statement SET TRANSACTION READ ONLY; then native procedure; finally rollback and close. No commit, begin_plan, row/policy lock, Stock prepare or hidden transaction switch. Dirty caller failure stops instead of clearing and continuing. Native procedure itself cannot attest caller read mode: direct arbitrary calls outside this port have NO consistency guarantee and are not an accepted producer. No snapshotSCN is fabricated. Frozen authority/state is as-of this read transaction. Revocation/composition changes after read are not blocked by a120-second informational expiry: future request/claim/capture/use MUST reauthorize and compare native closure under the existing owner lock order.

## Signature and references

Domain SHIPPING_GROSS/version1 is new and explicit; it is not ASM_FINAL/3, SMALL_HU/3, QC signature or existing HU digest. Signature input sorts projected physical nodes, links, compiled shipment domains and compiler resource declarations; recursively object keys use AL32UTF8 binary order. Explicit stable node fields exclude status/QC/packing timestamps/derived mass. Link IDs/versions, physical stock versions/quantities/UOM, case version/carrier, ST rows_signature and compiler-resolved reservation IDs/versions remain. Shipment nested legs retain existing deterministic compiler order; no allocation reordering/quantity calculation is introduced. Opaque resource keys include FF/ST/other declared row identities and some plan anchors, NOT claimed named FF versions or proof that a lock is held. Fixed compiler operation SHIPPING.GROSS.READ never creates an operation.

Native exact projection_json is retained; SHA256 is over that original UTF8 string. Python verifies byte-digest consistency and request/root/domain/expiry/bounds; it does not reserialize Oracle JSON, verify cryptographic authority, or approve quality. Native JSON sorting must be proved with reordered arrays/object-key/NLS fixtures before installation is accepted.

Bounds: HU200/depth16/physicalunits10000 inherited; projected links200/shipments200; sort arrays1000/elements32767characters, recursive JSON32, projection131072characters with Python stricter131072UTF8bytes, envelope262144bytes; caller timeout5seconds and120-second read expiry. Oversize rejects, never truncates or invents UNKNOWN mass. No mass data from browser, expected/observed calculation, actual capture or loading consumer in this candidate.

## Required acceptance before release

Root first reviews/compiles prepared sources with fresh immutable checkpoints, then pure native repeated/reordered/NLS identity test on isolated nonquantity HU fixtures. Compare source and table histories unchanged; test role WARE/GROUP/revoke/foreign/SELF, missing/ambiguous UID/scan/version, nested root/cycle/open task/missingQC, modified leaf/link/reservation/ST binding. Prove read-only port refuses any dirty/nested transaction and compiler has no side effects. Then measure bounded top SQL/closure plans. No successful Oracle/native or hardware acceptance is claimed by Python doubles.

Remaining full SHIPPING_GROSS: device/station admission; durable request/claim/zero/proper live permission; actual instrument capture and separate raw binding; immutable use; thermal compatibility; scoped loading/child QC policy; partial-store subtree handover. Existing quantity owners and MANUAL_CONFIRMED contract remain unchanged.
