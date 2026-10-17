# HU mass projection — read-only building block

Status: implemented pure Python projection only. SHIPPING_GROSS request/claim/capture/QC/loading integration remains proposed, not implemented here.

Prepared separately: native informational SHIPPING_GROSS read candidate plus Python port. **Not installed in Oracle, no API route.** Root review corrected use of locking `assert_allowed` to pure `allowed` with NULL denial, and rejects a borrowed dirty connection before the port's cleanup boundary. Original candidate retained in `reports/retailcase/2026-10-15/shipping-gross-read/root-review-before/`;15 boundary tests PASS. Full source/transitive review, installable guarded migration, live compile/auth/identity/side-effect/SQL acceptance remain prerequisites. The candidate is not an accepted producer for this projection.

Root native helper review found an additional canonicalization defect: Oracle `UTL_RAW.COMPARE` returns a mismatch position, not signed order. Corrected first-byte/length comparison passes17 synthetic pairs, reordered object/array and2NLS variants in anonymous PL/SQL; [native evidence](../../reports/retailcase/2026-10-15/shipping-gross-read/canonical-native-probe.json). Schema/package installation and business writes were absent.

Larger CLOB/merge-sort experiments remain **unreleased** in `tmp/`: one1000-item stress block with33024-character elements took5.14s/5.52s, beyond the port's5s call budget; combined boundary test timed out. These are algorithm-test timings, not shipment/endpoint p95. Do not substitute those experimental sources for the current reviewed candidate or call the bounds accepted. Quality/inventory owns stage-level JSON/LOB/sort profiling and explicit input bounds before native release. One early v5 helper JSON was mistakenly removed when extending its test; this loss is recorded in [timeout note](../../reports/retailcase/2026-10-15/shipping-gross-read/canonical-v5-boundary-timeout.json), not reconstructed as original evidence. v4 and later stress artifacts are retained.

Seven additional native bodies were captured read-only in [purity follow-up](../../reports/retailcase/2026-10-15/shipping-gross-read/purity-followup/manifest.json), INVALID0. HU_LOAD_CORE.compile_load immediately returns when this fixed request lacks loading_context, so its loading/thermal/floor writers are not invoked by this candidate. QC_POLICY settings/controller/sampling/full_scan and QC_WEIGHT calculate paths read current rows; full transitive audit is still incomplete. The candidate remains NOT INSTALLABLE.

### Additional bound and thermal findings

The suspected unbounded CASE placement-claim loop has a native cardinality proof:
`RRL_HU_CLAIM_CASE_U1` is a VALID UNIQUE NORMAL index on `HU_CASE_TASK_ID`.
For a non-null CASE ID, `declare_existing_case` can therefore visit at most one
row, even though its SELECT has no FETCH clause. The stock claim loop also has
the validated UNIQUE `RRL_REC_SLOT_PAL_UK(UID_PALLET)`. Do not add redundant limits
or widen those keys. Release guards must pin these indexes/columns/status together
with source versions. [Read-only exact-table metadata](../../reports/retailcase/2026-10-15/shipping-gross-read/claim-bound-metadata.json).

Metadata query timings: indexes109ms, columns118ms, expressions63ms,
USER_CONSTRAINTS3469ms. This is catalog verification, not shipment latency.
Operations/schema-verification owns the existing dictionary-plan/statistics
backlog; use exact index/name checks for release and avoid this broad constraint
projection in runtime. No business-table index is justified by catalog cost.

`RRL_INTERWARE_THERMAL.assert_cell` was captured and inspected: it parses the
supplied thermal mode and SELECTs the target cell rule; writer `record_decision`
is a separate procedure and is not called by this predicate. When both mode
bounds are null it returns without a thermal restriction. This does not establish
mixed vegetables/chilled compatibility or hardware temperature evidence.
[Native checkpoint](../../reports/retailcase/2026-10-15/shipping-gross-read/purity-thermal/manifest.json), INVALID0.
An initial capture request also named two nonexistent guessed guard packages
and failed before writing any checkpoint; only the exact existing package was
then captured. Full transitive purity/native acceptance and early global work
bounds remain open; late JSON array limits alone do not bound all compiler work.

Owner is the declared `quality` module. Current outgoing quality commands still belong to the existing inventory/native owners: `OutgoingQuality` / `OUTGOING_PALLET_CHECK`. Master-data `WeightPolicyInput` describes SKU nominal weight, while current transport/HU measurement DTOs accept MANUAL_CONFIRMED. None of those is replaced or silently reclassified as hardware evidence.

## Inputs and result

The typed immutable input consumes the existing native closure as a flat read projection: generic identifier, native content version/domain/signature version/hash, physical warehouse/cell, direct child identifiers and leaf stock keys. It adds references to existing archived observed gross, explicit estimates and own tare evidence. These are not new stock/HU entities or equipment capture DTOs.

A mandatory `producer_proof` is a traceable producer declaration. No Oracle adapter or cryptographic verification exists in this increment. The result always reports `producer_proof_verified=false` and `quality_release_approved=false`; callers cannot turn those flags on through constructor arguments.

For each parent the expected gross is the sum of the gross of its DIRECT children plus its OWN explicit tare/packing mass, once. A valid independently measured child gross is usable even when that child's expected calculation is unknown. If a child has no valid observation, its calculated/explicit estimated gross may be used, retaining the estimate flag. Missing child mass or missing own tare yields UNKNOWN; there is no default zero or proportional allocation.

An independent observed outer gross is retained unchanged even when expected gross is UNKNOWN, expired or stale. Root comparison requires explicit proposed source domain SHIPPING_GROSS/version 1, correct current binding, current evidence and a measurement no earlier than the original freeze. ASM_FINAL/3 and legacy SMALL_HU/3 do not become outer shipping measurements. The projection exposes an arithmetic difference only; it chooses no tolerance and grants no QC/loading approval.

A separate local `projection_sha256` fingerprints the supplied input and derived states; it is not the native closure signature or a certificate attestation. Root/current native identity mismatch or frozen-input expiry suppresses current calculations. Evidence timestamps and original values are never refreshed by retry/read.

## Structural and numerical checks

- Existing physical closure only: all nodes share actual warehouse/cell. A future consolidation dependency manifest is not accepted as a physical tree.
- At most 200 nodes, depth 16, unique parent/reachable nodes, no cycles/repeated child and no repeated leaf stock key. The 10000 bound applies to keys in this projection, not a new claim about quantity/physical-unit validation; that remains native owner responsibility.
- Decimal sources are finite/nonnegative,18digits/9decimals, with explicit KG/GROSS or TARE basis. Arithmetic uses sufficient local precision and does not depend on process Decimal context.
- Current versions, aware instants and explicit expiry are required. Validation and all temporal comparisons normalize to UTC, including DST folds; nonexistent local times are rejected through UTC roundtrip. A stale child observation remains historical and cannot silently contribute as current measured mass.

## Evidence and remaining work

[Implementation](../../api/wms_api_server/app/modules/quality/public.py) and [37 pure tests](../../tests/retailcase/test_quality_hu_mass_projection.py) cover direct-child versus all-level summation, unknown child with measured outer, estimates, missing tare, invalid/future/expired facts, native composition change, wrong domain, tree violations and exact Decimal arithmetic.

Native closure/archive adapter, current authority/proof verification, SHIPPING_GROSS request/claim/zero/capture archive, immutable capture-use, native tolerance/QC and loading consumer remain pending root review. This module creates no routes, DB objects, stock writes, external calls or physical-hardware evidence.

Related: [[retailcase_nested_hu_consolidation_20261015]], [SHIPPING_GROSS design](../../docs/integrations/shipping-gross-proposed.md).

## Bounded native integration proposal

The current `RRL_STOCK_PALLET_QC_CMD` WEIGHT/WEIGHT2 compares gross minus wood tare against native SKU expected NET/tolerance. It is not the same calculation as a whole-HU expected GROSS. The projection does not reimplement that tolerance/QC decision or feed an outer gross into every child ST.

A subsequent reviewed increment must:

1. Freeze SHIPPING_GROSS domain/version over the existing native HU closure, actual warehouse/cell, child versions, current fulfilment/ST/reservations and explicit packaging/tare evidence. Existing native hash remains authoritative; this Python fingerprint is not its replacement.
2. Add a separate whole-HU equipment capture/claim/archive purpose and immutable native capture-use. Preserve existing CASE/ASM/store canonical bodies and the shared physical device lease; gateway input never chooses shipment membership.
3. Add an explicit hardware-source alternative to the current loading source. `RRL_STOCK_HU_LOAD_CORE` currently accepts MANUAL_CONFIRMED and stores frozen COMPOSITION_JSON; the new source must resolve actual mass from the archive under current owner locks, rather than accept browser mass. Dimensions remain separate evidence.
4. Define native mass tolerance and expiry policy for whole-HU gross. Aggregate mass approval cannot replace child per-ST composition/QC guards. Current `LOAD_BOX_CORE` only checks coverage/lower bounds and preserves existing warehouse CASE QC or manual box provenance; it is not recursive expected-gross equality.
5. Admit thermal compatibility, destination zone and current scoped HU authorization through their existing native owners. Multiple-store route pallets need subtree handover identity; full outer gross never becomes a partial store's expected gross.
6. Verify raw archive binding and exact capture/use/loading replay in the same existing native stock-operation boundary. Archive/capture HTTP ACKs alone are not an atomic business-release guarantee.

No native/API/quantity implementation of these six points is included in the pure projection.

A fact binding is the producer-declared current association resolved by the native owner. It must not be fabricated by changing the binding of an old archive after MOVE/ATTACH. In particular, an earlier empty-tare archive can contribute only through a valid explicit current native tare-use/packaging association; without that adapter proof the projection must remain UNKNOWN. The original capture body and measurement time remain unchanged.

## Native read candidate v7 checkpoint

Not installed. Existing candidate body now uses canonical DOM references, merge sort and cached AL32UTF8 keys, with per-sort early size/work rejection. Evidence: `reports/retailcase/2026-10-15/shipping-gross-read/canonical-native-probe-v7-split.json` (17binary pairs, two NLS, separate0/1/999/1000 cases, max4849ms cold anonymous compile, warm1000 731/676ms); `canonical-native-v7-bounds.json` (5checks,9-610ms), `v7-bounds-watchdog.json`. Original uninstrumented bounds client overran and was terminated; the successful instrumented repeat does not explain that initial wall overrun. Combined all-sizes call exceeded5000ms and is not a PASS. No business SQL/DDL in helper probes. Decision: retain bounded DOM/key optimization, no index/cache change; measure full compiler fan-out and freeze CPU budget before installation. Full transitive purity/release kit, freeze, device request/claim/zero/capture/use and loading/QC remain open. Current thermal SHIP guard must join the fresh source checkpoint.

## V8: expected membership binding

Не установлен. После [[../database/retailcase_consolidation_manifest_20261016]] проекция содержит native consolidation token: plan ID/version/expectation hash либо явный null. Изменение ожидаемого состава должно менять freeze даже при неизменном физическом дереве. Canonical helper prefix v7 побайтно сохранён; повторный benchmark не запускался. [Прежний v7](../../reports/retailcase/2026-10-16/consolidation-manifest/gross-v7-before/candidate-manifest.json) сохранён. Для полного purity/release требуются актуальные HU_SHIP и RRL_HU_CONSOL_READ; metadata-writing API не входит в read path. Capture/use/QC/loading остаются открытыми.

Python read contract теперь выдаёт отдельный immutable ShippingGrossExpectations
и требует явный null либо корректный token. Отсутствующее поле, неверные типы,
domain/version/подпись не превращаются в legacy unconfigured.26 адресных проверок
PASS, общий quality gate PASS; это wire/UOW checks, не native freeze acceptance.
Fresh8 current sources/INVALID0: [checkpoint](../../reports/retailcase/2026-10-16/shipping-gross-current/manifest.json).
