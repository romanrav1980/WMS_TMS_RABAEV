# C-0187 — T06: tests for the CASE write paths by weight

## What is covered
`tests/retailcase/test_weighted_case_pick.py`, 36 tests, offline. It uses a fake Oracle cursor/gateway and a recording StockPosting port; no database writes. The mocked capture or scan is a contract test, not hardware or live weight evidence.

1. **weigh-line (NET capture):**
   - the capture of exactly this task/line → one CASE_PICK_CONFIRM with the cumulative `fact_qty` (1.25+2.5=3.75) and `warehouse_scale_capture`;
   - access is checked through `RRL_CASE_TASK_ACCESS.assert_scope(task, actor, 'case_pick_execute')`; the read is bound to p_key/p_task/p_line and `MEASUREMENT_BASIS='NET'`;
   - a capture of another line, missing or not NET → ValueError, nothing posted;
   - access denied (20882/20886) → `WEIGHED_CASE_SOURCE_REJECTED` with oracle_code, nothing posted;
   - a malformed capture key → rejected by the contract (pattern).
2. **Repeat/conflict:**
   - an exact repeat → the stored metadata, with no source read and one posting call; idempotency is then StockPosting's job;
   - a different capture, actor, task, line or body, or a weighted-box operation under the weigh-line route → `OPERATION_CONTENT_CONFLICT`, nothing posted.
3. **weighted-box:**
   - a valid box reserved for this line → exactly one posting, units=(physical key), fact_qty 1.5+2.345, policy version recorded, `assert_sku(article,gtin)` called;
   - rejected, with nothing posted:
     - a box not reserved for the line, or ambiguous (0 or 2 rows);
     - another SKU (native GTIN check 20886);
     - KG mismatch or a non-KG unit;
     - a required marking not scanned, a duplicate marking scan, marking scanned on an unmarked SKU, or a stale policy/profile (marking required without a current profile);
     - a marking of another physical unit;
     - a malformed label (decode 20886/1403) → `WEIGHTED_BOX_SCAN_REJECTED`;
   - a repeated barcode after posting: the query excludes `STOCK_STATUS='ISSUED'`, so the box is not found again;
   - weighted-box repeat/conflict.
4. **Routes:**
   - both POSTs require `case_pick_execute`: 403 without it, and the service is not called;
   - ValueError → 409 `{code, message, outcome_confirmed:true, retry_same_operation_id:false}`;
   - StockPostingError through the global handler: 20882 → 403 confirmed; OPERATION_CONTENT_CONFLICT → 409 outcome_confirmed=false; RESULT_UNCERTAIN → 503 retry_same_operation_id=true;
   - an extra field (`weight_kg`) → 422 before the service.

**Defects:** none found. Production code is unchanged.

## Review: one parent HU tree with both sources (read-only, `RRL_STOCK_HU_CMD` live + `warehouse_hu_routes.py`)
- Both weight paths credit goods to the CASE task's carrier (`scan_container`) through CASE_PICK_CONFIRM. A weighed line (NET capture) and a weighted box can be lines of the **same** CASE task (the policy is per SKU), and so can ordinary box or each lines.
- **What can be attached to a parent HU:**
  - `POST /api/warehouse-hu/attach-case` (CaseLink: `child_case_task_id`) attaches a whole CASE task with its carrier;
  - `POST /attach` (Link: `child_uid`) attaches a child HU.
- **Native HU_ATTACH guards:**
  - the parent is a CONTAINER;
  - the same cell and warehouse;
  - expected_version and expected_child_version;
  - no cycle;
  - the child has no parent yet;
  - ≤200 nodes;
  - an unslotted work area;
  - a scan of the child (for CASE, the carrier's SSCC: `HU_CASE_CARRIER_SCAN_REQUIRED`);
  - `RRL_STOCK_CASE_BIND_MOVE.validate_tree`, the current temperature check, and trade guards (for example `TRADE_MIXED_PALLET_BLOCKED` for owners).
- **Shape allowed today:** a parent HU container ← N children, each either a CASE task (with weighed, weighted-box and box/each lines in any combination per SKU) or an HU; all at one location, each child scanned and with its version.
- **Missing for the owner's mixed tree** (manual weighed assembly + box/each pick from a shelf), not proven here:
  - there is no automated/live acceptance of the combined tree "a CASE with a weighed line + a CASE with box picks → one parent";
  - weighed assembly outside a CASE task (manual weighing without a CASE line) has no attach path of its own: the weight source must be a CASE line with a NET capture;
  - the parent's total gross weight is confirmed separately (`Measurements origin=MANUAL_CONFIRMED` on HU move), not computed from the children.
  - The HU guards were not changed or weakened.

## Checks (commands)
- `python -m pytest -q -p no:cacheprovider tests/retailcase/test_weighted_case_pick.py` → 36 passed
- `python scripts/retailcase_quality_gate.py` → PASS
- `powershell -ExecutionPolicy Bypass -File scripts/check-encoding.ps1` → PASS
- `python scripts/check_architecture.py` → PASS (cycles 0)
- The broader suite was not run (no production changes). No live writes; the API was not restarted.
