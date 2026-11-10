# C0195: one root pallet, several orders of one recipient (strategic analysis)

Analysis only: no code, tests, Oracle or API writes. Sources are the repository bodies as of 28.10 (cited inline) and the fixture evidence `runtime/test-evidence/tradecase/2026-10-28/T06/mixed-tree/root-tare-order.json`. Nothing below has been run.

## 1. Fixture MT285C7190E3A (facts from evidence)

- **Root:** `MT285C7190E3A.PAL`, a CONTAINER/PALLET at version 2 in cell `CPT_237807733`, warehouse 237807733. Its root tare booking `MT285C7190E3A.ROOT.TARE.BOOK` is HELD.
- **CASE children** (both WAIT_CONTROL, version 2, both in the root's cell):

| CASE | Order | Goods | Fulfillment |
|---|---|---|---|
| 1185 | 2248 | KG 9.6 | 1602 |
| 1184 | 2249 | EA 4 | 1603 |

- **ST:** 643011, `MT285C7190E3A.ST.PAL`. Rows: KG 9.6 and EA 4. CONDITION 0, one address. Fixture customer `-980702` for both orders.
- **Binding:** C0193 root binding `MT285C7190E3A.T.BIND.ROOT` returned `BOUND`. Both CASEs now point to 643011, and each fulfillment is PICKED with `PICKED_CASE_TASK_ID` and its own composition.
- **Run stage:** `FLOOR_QC_TARE`, so neither QC nor loading has run yet.

**Predicted from source (not observed):** the next step, the QC status read, fails on this ST, and so would `HU_SHIP`. Both call `RRL_STOCK_SHIPPING_CORE.compile_shipment(SHIP_PALLET)`, which refuses an ST with more than one order: `SHIPMENT_CUSTOMER_ORDER_AMBIGUOUS` (`db/migrations/2026-10-16_full_shipping_scope/rrl_stock_shipping_core_package_body.sql:30-31`). Even past that check, `select … into … from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID=v_id` (`:47-48`) raises TOO_MANY_ROWS for two CASEs. That is an unmapped ORA-01422, not a business refusal.

## 2. Single-order assumptions in today's code

| Place | Assumption |
|---|---|
| `SHIPPING_CORE.compile_shipment` | one `customer_order_id`, one `case_task` per ST; reservations filtered by that one order and that CASE's lots; `CASE_SHIPMENT_CONTENT_MISMATCH` compares legs with one carrier |
| `SHIPPING_CORE.execute_resolved` | locks and re-checks one order and one CASE; `project_ship(st, uid, order, …)` once, with all legs; one CASE → SHIPPED |
| `RRL_STOCK_FULFILLMENT_FACT.project_ship` | exactly one fulfillment per (ST, uid, order), else `SHIPMENT_FULFILLMENT_AMBIGUOUS`; stores the facts it is given as that fulfillment's shipped composition |
| `RRL_STOCK_QC_GATE.signature_for_plan` / `signature_version_for_plan` / `status_json` | signature includes one `customer_order` and, for version 3, one CASE's SSCC/type; `status_json` builds its domain through `compile_shipment` |
| `RRL_STOCK_HU_SHIP_CMD.compile_command` (`…/rrl_stock_hu_ship_cmd_package_body.sql:41-79`) | **already** groups CASE children by distinct `LEGACY_SBORKA_PALLET_ID`, calls `compile_shipment` once per ST, runs `QC_GATE.assert_approved` per ST, and requires every STOCK leaf of the tree to be consumed exactly (`HU_SHIP_WHOLE_PHYSICAL_LEAF_BINDING_REQUIRED`). The tree-to-ST bridge exists; only the per-ST compile is single-order. |

## 3. Minimum safe transaction boundary

**Use the existing `HU_SHIP` posting operation, unchanged as a boundary.** That means one `RRL_STOCK_OPERATION`, one root write context and one database transaction for the whole root.

**Extend only `RRL_STOCK_SHIPPING_CORE`,** so that one ST can produce a *multi-order domain*. This should be a new internal branch, entered only when the ST has more than one order. The existing one-order branch stays byte-for-byte as it is.

### 3.1 Entry conditions (all checked in compile, then again under locks in execute)
The multi-order branch is used only when **all** of the following hold. Otherwise it refuses with a precise code, never an ORA error.

1. The ST has ≥2 distinct orders, and every ST fulfillment is `PICKED` with a `PICKED_CASE_TASK_ID`, exactly one per order.
   - Refusals: `SHIPMENT_MULTI_ORDER_FULFILLMENT_NOT_PICKED_PER_CASE`, `SHIPMENT_FULFILLMENT_AMBIGUOUS`.
2. The set of CASE tasks with `LEGACY_SBORKA_PALLET_ID = ST` equals the set of `PICKED_CASE_TASK_ID`s.
   - Each CASE's `CUSTOMER_ORDER_ID` equals its fulfillment's order, the CASE warehouse equals the ST warehouse, and the CASE status is in the closed set.
   - Refusal: `SHIPMENT_MULTI_ORDER_CASE_SET_MISMATCH`.
3. **One root.** Every CASE has an active link to the same top-level CONTAINER, all in one cell, and that root holds no CASE bound to another ST.
   - Refusal: `SHIPMENT_MULTI_ORDER_ROOT_SPLIT`.
   - The owner rule is one root ↔ one ST ↔ one recipient.
4. **One recipient.** All orders have the same `CUSTOMER_ID`, and every fulfillment's `ADDRESS_TEXT`, trimmed, equals `RRL_SBORKA_PALLETS.ADDR`. No order is CANCELLED and no fulfillment is SHIPPED or CANCELLED.
   - Refusals: `SHIPMENT_MULTI_ORDER_RECIPIENT_CONFLICT`, `SHIPMENT_CUSTOMER_FULFILLMENT_CLOSED`.
5. **Not a supplier return or interwarehouse onward ST:** `SUPPLIER_RETURN_CUSTOMER_SOURCE_CONFLICT` and `INTERWARE_ONWARD_NO_DUPLICATE_CUSTOMER_FULFILLMENT` stay as they are.

### 3.2 Per-CASE validation (each against its own order and fulfillment)
For each CASE (slice), reuse the current single-CASE rules with `order := that CASE's order`:
- Demand comes from `RRL_STOCK_CASE_PICK_CMD.carrier_rows(case)`, not from the ST rows.
- Allocate only that order's HARD/PICKING reservations on that CASE's carrier lots, with that order's DONE pick task. This is the existing predicate at `:105-112`, with `v_customer_order` and `v_case_task` taken per slice.
- The allocated quantity per lot must equal the carrier quantity: `CASE_SHIPMENT_CONTENT_MISMATCH`, reported per CASE.
- The fulfillment's `PICKED_CONTENT_VERSION` must equal the CASE's `CONTENT_VERSION`, and its `FACT_COMPOSITION_JSON` must equal the carrier composition in base units: `SHIPMENT_MULTI_ORDER_FULFILLMENT_CHANGED`.
- Every leg carries its own `customer_order_id`, `case_task` and `fulfillment_id`.

### 3.3 Aggregate ST composition
- The sum of all slices' carrier quantities per (article, base UOM) must equal the ST rows converted to base, using the existing UOM conversion at `:97-100`. There must be no missing, extra or partial row: `SHIPMENT_MULTI_ORDER_COMPOSITION_MISMATCH`.
- `rows_signature` stays frozen as today.
- Each leg keeps `row_id` = the ST row of its article and base UOM. Two orders sharing one article may point to the same row, and `consume` accepts that.
- The bound of 200 legs is unchanged.

### 3.4 Domain shape (compatible)
Multi-order domain:
- `customer_order_id = null`, `case_task = null`;
- a new `multi_order: {version:1, slices:[{customer_order_id, fulfillment_id, case_task, case_version, case_cell, case_carrier}]}`;
- `legs[]`, each with `customer_order_id`, `case_task` and `fulfillment_id`.

Effect on existing consumers:
- **`RRL_STOCK_QC_CASE.nested(domain)` must return 1** for `multi_order`. Then `execute_resolved` already refuses any root other than `HU_SHIP` (`SHIPMENT_WHOLE_HU_REQUIRED`, `:233`). Plain `SHIP_PALLET` and single-ST `LOAD_SHIPMENT` can never ship part of a multi-order ST.
- **`HU_SHIP` needs no change.** Both CASEs share one ST, so it makes one `compile_shipment` call, one `assert_approved`, and one `execute_resolved`. Its whole-leaf check covers the full root.

### 3.5 Execute (inside the same HU_SHIP transaction)
1. **Lock in canonical order:**
   - ST row, then order rows ascending, fulfillments ascending, CASE tasks ascending, then reservations;
   - each must also be declared as a plan resource in compile.
2. **Re-check under locks:** all of §3.1–3.3 against the frozen domain (`CLOSURE_CHANGED: …` on any drift).
3. **QC:** `QC_GATE.assert_approved(domain)` and `record_exemption` run once per ST, as today.
4. **Consume per leg.** The reservation check uses the leg's own order: `sr.CUSTOMER_ORDER_ID = leg.customer_order_id` replaces the domain-level value at `:303`.
5. **Ship the ST once:** `RRL_SBORKA_PALLETS.CONDITION=2`.
6. **Per slice:**
   - **Project the fulfillment with only that slice's facts.** Proposed `project_ship_case(st, uid, order, case, op, facts, actor)` matches the fulfillment by `CUSTOMER_ORDER_ID` **and** `PICKED_CASE_TASK_ID`. The existing `project_ship` stays for one-order STs.
   - **Close the CASE:** `release_case` and CASE → SHIPPED.
7. **Result:** one result with `allocations` plus `slices[{order, fulfillment, case, allocations}]`.

### 3.6 Idempotency
- **Replay:** no new journal. The `HU_SHIP` operation id is the only key, with the same posting-root `OP` and `STOCK.OUTBOX` anchors.
  - An exact replay returns the stored result.
  - A changed body gives `OPERATION_CONFLICT`.
  - A changed tree or ST gives `CLOSURE_CHANGED`, which is still atomic because nothing is written.
- **Reruns:** a second `HU_SHIP` after success fails on `SHIPMENT_ALREADY_CLOSED_WITH_OTHER_OPERATION` (CONDITION=2) and on CASE status.
- **Partial outcome:** none is possible, because all slices commit or none do.

### 3.7 QC signature (keep one-order STs unchanged)
- **Single-order signature:** unchanged byte-for-byte. Existing approved QC stays valid.
- **Multi-order signature:** the same fields, plus `orders:[{order, case, case_sscc, case_type_id}]` sorted by order, with `customer_order=null`.
- **Version 3** (final weight of a container CASE) applies only when every slice CASE type requires it. Otherwise version 2, which root should confirm.
- **`status_json`:** works once compile supports multi-order. It should add `slices` for the UI.

## 4. One-order ST behaviour is not weakened
- **Branch gate:** the branch starts only at `v_order_count > 1`. That path refuses today, so no currently succeeding shipment changes route.
- **Golden-domain guard:** for `v_order_count ≤ 1`, the code and domain JSON stay as they are. A regression test should compare the compiled domain and QC signature of existing one-order fixtures (CASE, full-pallet, non-CASE, supplier return, interwarehouse) before and after.
- **No direct shipping of a multi-order ST:** a multi-order ST can never ship through `SHIP_PALLET` or `LOAD_SHIPMENT` alone, only as a whole root through `HU_SHIP`.

## 5. Audit surface before implementation (not verified here)
1. **Domain consumers to check:**
   - `RRL_STOCK_QC_POLICY` (`settings_for_plan`, `full_scan_required`, `controller_allowed`);
   - `RRL_STOCK_QC_MARK.required_for_plan`;
   - `RRL_STOCK_QC_WEIGHT.calculate`;
   - `RRL_QC_SCOPE_READ` (`policy_json`, `exemption_json`, `record_exemption`);
   - `RRL_WH_FINAL_SCALE_ADMISSION.approved`;
   - `RRL_STOCK_QC_CASE.nested`;
   - `RRL_STOCK_LOADING_READ.assert_scope`.

   Each reads the domain. Any that uses `case_task` or `customer_order_id` must iterate `multi_order.slices` instead of treating null as "not a CASE". In particular, a CASE's own weight or mark rules must not silently fall back to non-CASE policy.
2. **Unload/return:** `FULFILLMENT_FACT`'s unload branch already matches by `PICKED_CASE_TASK_ID` per fulfillment (`53_package_bodies.sql`, `project_ship` neighbours). It must restore each slice separately.
3. **QC weight of the whole root:** expected weight = Σ slices + root tare (`tare_weight_kg` 20 in the fixture). Confirm how `QC_WEIGHT.calculate` treats the container tare on a multi-order ST.

## 6. Rejected alternatives
- **Split one root into one ST per order:** violates the owner rule of one root, one ST and one recipient.
- **Relax `SHIPMENT_CUSTOMER_ORDER_AMBIGUOUS` to `min(order)`:** allocates against the wrong order's reservations. Unsafe.
- **Python orchestration of several posting operations:** not atomic, and an exact replay is lost across steps.
- **A new table or journal:** unnecessary, since the posting root already gives atomicity and replay.

## 7. Not claimed
No implementation, test or live run. The refusal codes are proposals. The fixture failure in §1 is predicted from source, not observed.
