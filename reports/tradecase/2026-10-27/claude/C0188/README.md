# C-0188 — T06: manual NET weighing of a CASE line

## Native authority (read-only, confirmed; review K-0211)
- **Writer:** the single writer is `CASE_PICK_CONFIRM` (RRL_STOCK_CASE_PICK_CMD through StockPosting). The canonical request in RRL_STOCK_OPERATION is the immutable, idempotent record: actor, source {case_task_id, case_line_id}, metadata, operation_id, time.
- **Scale optional:** `RRL_CASE_SCALE_ADMISSION.assert_capture/claim_capture` return immediately without `warehouse_scale_capture`. `RRL_CASE_WEIGHT_SCAN.assert_scan` applies only to SERIALIZED_WEIGHT_BOXES.
- **Native guards stay in force:** actor/assignment, LAUNCHED, task/line status, previous_qty closure, fact>previous and ≤PLANNED_QTY, carrier/cell/product scan, own HARD, CASE_MARKED_UNIT_SCANS_REQUIRED.
- **Metadata keys:** there is no whitelist in native (checked in user_source) and none in the Python StockCommand. The new provenance keys are passed through as they are, which matches the ACK. No DDL.

## Change (owned Python files only)
- `contracts_weighted_case.py`: `ManualNetLineRequest` (extra=forbid): `operation_id`, `net_weight_kg` (Decimal >0, finite, `max_digits=27, decimal_places=9`, the same as the existing CASE `fact_qty` contract), `scan_cell`, `scan_container`, optional `unit_scans` (≤50, for marked SKUs). The port method is `weigh_line_manual`.
- `api/weighted_case_routes.py`: `POST /api/case-pick/tasks/{task}/lines/{line}/weigh-line-manual`, `case_pick_execute`; ValueError → 409 `WEIGHED_CASE_MANUAL_REJECTED` (outcome_confirmed=true).
- `infrastructure/weighted_case_pick.py`:
  - `weigh_line_manual` + `prepare_manual_net`;
  - a fresh read-only read under `assert_scope(task, actor, 'case_pick_execute')` of exactly the task/line;
  - only a genuine KG NET line: the KG→KG 1:1 conversion, as in native scale admission, and not SERIALIZED_WEIGHT_BOXES (those go through `weighted-box`);
  - `fact_qty = PICKED_QTY + net_weight_kg` computed on the server; `scan_product` from the line; marking scans → `resolve_case_codes` → units (native decides on them);
  - metadata `measurement={basis:NET, uom:KG, net_weight_kg, origin:MANUAL_OPERATOR_ENTRY}` and `manual_net_confirmation=<request>`;
  - repeat via the canonical request; any change → OPERATION_CONTENT_CONFLICT.
- The electronic `/weigh-line`, `WeighedLineRequest`, the weighted-box path and the general legacy confirm are not changed.

## Tests
`tests/retailcase/test_weighted_case_pick.py`: **57 passed** (36 earlier + 21 new for C0188). New ones:
- a valid KG line → one posting, fact 1.5+1.237=2.737, provenance, no scale capture, scope check with case_pick_execute, binds exactly to the task/line;
- missing line or another task, non-KG, serialized → refusal without posting; access denied 20882/20886 → `WEIGHED_CASE_MANUAL_REJECTED` without posting;
- marking scans → physical units in the command;
- contract: 0/negative/NaN/Infinity/more than 9 decimals rejected; the manual variant cannot carry `warehouse_scale_capture` or `fact_qty`, and the electronic one cannot carry `net_weight_kg` (the sources are mutually exclusive);
- exact repeat → the stored operation without reading the source; a different net/actor/task/line/body → conflict; an operation of the electronic route under the manual route → conflict;
- route: 403 without case_pick_execute; 409 confirmed refusal; RESULT_UNCERTAIN after commit → 503 `retry_same_operation_id=true` (repeat with the same operation); an extra field → 422.

## Checks (commands)
- `python -m pytest -q -p no:cacheprovider tests/retailcase/test_weighted_case_pick.py` → 57 passed
- `python scripts/retailcase_quality_gate.py` → PASS
- `python scripts/check_architecture.py` → PASS (cycles 0)
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-encoding.ps1` → PASS
- No Oracle writes; the API was not restarted (the new route reaches the served API only after root restarts it).

## Gap in the general path (reported, not rewritten)
`CasePickLineConfirmRequest` (the general CASE confirm, `schemas.py`) accepts a client `fact_qty` for a KG line without a scale and without provenance, and native allows it (assert_capture is skipped without a capture). So the same product can still be confirmed by the old path with no record of the weight source. This needs a separate decision: for example, forbid the general path for KG NET lines, or require provenance.

## Limitations
- T06 is not complete: there is no live Oracle/API acceptance of the manual route (owned QA line, posting, repeat, conflict, residual stock).
- A manual entry is the operator's declared value, not a scale reading.
